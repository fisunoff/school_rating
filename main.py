from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.sql import null

from forms.product import ProductsForm
from forms.balance import AddBalanceForm, CheckOperation
from forms.user import RegisterForm, LoginForm
from forms.event import EventsForm
from data.products import Products
from data.events import Events
from data.orders import Orders
from data.users import User
#from data.qiwi_api import Payments
from data.super_admins import super_admins_ids
from data import db_session, products_api

import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(401)
def need_registration(_):
    return render_template("need_registration.html", title="Требуется регистрация")


def main():
    db_session.global_init("db/main.db")
    app.register_blueprint(products_api.blueprint)
    app.run()


@app.route("/")
@app.route("/main")
@app.route("/main/<sort_type>")
def index(sort_type="default"):
    db_sess = db_session.create_session()
    events = db_sess.query(Events)
    if sort_type == "sorted_by_name":
        events = [i for i in sorted(events, key=lambda x: x.event_name)]
    elif sort_type == "sorted_by_value":
        events = [i for i in sorted(events, key=lambda x: x.value)]
    elif sort_type == "sorted_by_event_date":
        events = [i for i in sorted(events, reverse=True, key=lambda x: x.event_date)]
    elif sort_type == "sorted_by_add_date":
        events = [i for i in sorted(events, key=lambda x: x.event_add_date)]
    elif sort_type == "sorted_by_author":
        events = [i for i in sorted(events, key=lambda x: x.author_id)]

    return render_template("index.html", events=events, title="Главная", super_admins=super_admins_ids)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            role="sell" if form.role.data else "buy"
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add_event", methods=['GET', 'POST'])
def add_event():
    form = EventsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        events = Events()
        events.event_name = form.event_name.data
        events.event_date = form.event_date.data
        events.value = form.value.data
        events.ids = form.ids.data
        events.annotation = form.annotation.data
        current_user.events.append(events)
        db_sess.merge(events)
        db_sess.commit()
        return redirect('/')
    return render_template('events.html', title='Добавление товара', form=form)


@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    form = EventsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter((Events.id == id),
                                ((Events.author == current_user) | (current_user.id in super_admins_ids))).first()
        if events:
            form.event_name.data = events.event_name
            form.event_date.data = events.event_date
            form.value.data = events.value
            form.ids.data = events.ids
            form.annotation.data = events.annotation
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        events = db_sess.query(Events).filter((Events.id == id),
                                                  ((Events.author == current_user) | (
                                                          current_user.id in super_admins_ids))).first()
        if events:
            events.event_name = form.event_name.data
            events.event_date = form.event_date.data
            events.value = form.value.data
            events.ids = form.ids.data
            events.annotation = form.annotation.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('events.html', title='Редактирование события', form=form)


@app.route('/event_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    events = db_sess.query(Events).filter((Events.id == id),
                                              ((Events.author == current_user) | (
                                                      current_user.id in super_admins_ids))).first()
    if events:
        db_sess.delete(events)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/event/<int:id>', methods=['GET', 'POST'])
def product_page(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Events).filter((Events.id == id)).first()
    return render_template("event.html", item=product, title="Просмотр карточки события")


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    db_sess = db_session.create_session()
    cart_db = db_sess.query(User).filter((User.id == current_user.id)).first()
    cart_db_cart = eval(cart_db.cart)
    products = db_sess.query(Products)
    price_all = 0
    for i in products:
        if i.id in cart_db_cart.keys():
            price_all += i.price * cart_db_cart[i.id]
    return render_template("cart.html", item=cart_db, cart_db=eval(cart_db.cart), products=products,
                           price_all=price_all, balance=cart_db.balance, title="Корзина")


@app.route('/add_to_cart/<user_id>/<item_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(user_id, item_id):
    db_sess = db_session.create_session()
    cart_db = db_sess.query(User).filter((User.id == current_user.id)).first()
    products = db_sess.query(Products).filter((Products.id == item_id)).first()
    if int(products.quantity) < 1:
        return redirect(f"/add_to_cart_error/{products.id}")
    cart_now = eval(cart_db.cart)
    if int(item_id) in cart_now.keys():
        cart_now[int(item_id)] += 1
    else:
        cart_now[int(item_id)] = 1
    cart_db.cart = str(cart_now)
    products.quantity -= 1
    db_sess.commit()
    return redirect("/add_to_cart_success")


@app.route('/add_to_cart_success', methods=['GET', 'POST'])
def add_to_cart_success():
    return render_template("add_to_cart_success.html", title="Интернет-магазин")


@app.route('/add_to_cart_error/<product_id>', methods=['GET', 'POST'])
def add_to_cart_error(product_id):
    return render_template("add_to_cart_error.html", product_id=product_id, title="Интернет-магазин")


@app.route('/delete_from_cart/<item_id>', methods=['GET', 'POST'])
@login_required
def delete_from_cart(item_id):
    db_sess = db_session.create_session()
    cart_db = db_sess.query(User).filter((User.id == current_user.id)).first()
    products = db_sess.query(Products).filter((Products.id == item_id)).first()
    cart_now = eval(cart_db.cart)
    if int(item_id) in cart_now.keys():
        products.quantity += cart_now[int(item_id)]
        cart_now[int(item_id)] = 0
    cart_db.cart = str(cart_now)

    db_sess.commit()
    return redirect("/cart")


@app.route('/put_on_balance/<amount>', methods=['GET', 'POST'])
@login_required
def put_on_balance(amount):
    db_sess = db_session.create_session()
    cart_db = db_sess.query(User).filter((User.id == current_user.id)).first()
    cart_db.balance += int(amount)
    db_sess.commit()

    return render_template("/balance_updated.html", money_col=amount)


@app.route('/add_money', methods=['GET', 'POST'])
@login_required
def add_money():
    form = AddBalanceForm()
    if form.validate_on_submit():
        amount = form.amount.data
        return redirect(f"/deposit_money/{amount}")
    return render_template('add_money.html', title='Пополнение баланса', form=form)



@app.route('/accept_cart/', methods=['GET', 'POST'])
@login_required
def accept_cart():
    price_all = 0
    cart_list = {}

    db_sess = db_session.create_session()
    orders = Orders()

    cart_db = db_sess.query(User).filter((User.id == current_user.id)).first()
    cart_db_cart = eval(cart_db.cart)
    products = db_sess.query(Products)

    for i in products:
        if i.id in cart_db_cart.keys():
            cart_list[i.title] = cart_db_cart[i.id]
            price_all += i.price * cart_db_cart[i.id]
    cart_list["price"] = price_all
    orders.products = str(cart_list)

    if int(cart_db.balance) < price_all:
        return render_template("/not_enough_money.html")

    current_user.orders.append(orders)
    db_sess.merge(current_user)
    db_sess.commit()

    db_sess = db_session.create_session()
    cart_db = db_sess.query(User).filter((User.id == current_user.id)).first()
    cart_db.balance -= price_all
    cart_db.cart = "{}"

    db_sess.commit()

    return render_template("/order_created.html", title="Заказ создан")


@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    db_sess = db_session.create_session()
    if current_user.id in super_admins_ids:
        orders_db = db_sess.query(Orders).all()  # Супер-админу доступны все заказы пользователей
    else:
        orders_db = db_sess.query(Orders).filter((Orders.user_id == current_user.id)).all()
    d = []
    for i in orders_db:
        d.append({"id": i.id, "products": eval(i.products), "date": i.order_time, "status": i.status})
    return render_template("orders.html", orders=d, title="Заказы", super_admins_ids=super_admins_ids)


@app.route('/edit_order_status/<order_id>/<status>', methods=['GET', 'POST'])
@login_required
def edit_order_status(order_id, status):
    status_types = {"1": "В обработке", "2": "Доставляется", "3": "Доставлено!",
                    "error": "Что-то пошло не так! Свяжитесь с технической поддержкой!"}
    db_sess = db_session.create_session()
    if current_user.id in super_admins_ids:  # Только для супер-админа
        orders_db = db_sess.query(Orders).filter(Orders.id == order_id).first()
    else:
        return redirect("/")
    orders_db.status = status_types[status]
    db_sess.commit()
    return redirect("/orders")


@app.route('/support', methods=['GET', 'POST'])
def support():
    return render_template("support.html")


if __name__ == '__main__':
    main()
