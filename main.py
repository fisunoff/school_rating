from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.product import ProductsForm
from forms.user import RegisterForm, LoginForm
from data.products import Products
from data.users import User
from data import db_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/main.db")
    app.run()


@app.route("/")
@app.route("/main")
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Products)
    return render_template("index.html", products=products)


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
            about=form.about.data
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


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        products = Products()
        products.title = form.title.data
        products.quantity = form.quantity.data
        products.price = form.price.data
        products.description = form.description.data
        products.category = form.category.data
        current_user.products.append(products)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('products.html', title='Добавление товара', form=form)


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    form = ProductsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        products = db_sess.query(Products).filter((Products.id == id),
                                                  ((Products.user == current_user) | (current_user.id == 1))).first()
        if products:
            form.title.data = products.title
            form.quantity.data = products.quantity
            form.price.data = products.price
            form.description.data = products.description
            form.category.data = products.category
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        products = db_sess.query(Products).filter((Products.id == id),
                                                  ((Products.user == current_user) | (current_user.id == 1))).first()
        if products:
            products.title = form.title.data
            products.quantity = form.quantity.data
            products.price = form.price.data
            products.description = form.description.data
            products.category = form.category.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('products.html', title='Редактирование товара', form=form)


@app.route('/product_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    products = db_sess.query(Products).filter((Products.id == id),
                                              ((Products.user == current_user) | (current_user.id == 1))).first()
    if products:
        db_sess.delete(products)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/product/<int:id>', methods=['GET', 'POST'])
def product_page(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Products).filter((Products.id == id)).first()
    return render_template("product.html", item=product)


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
                           price_all=price_all)


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
    return render_template("add_to_cart_success.html")


@app.route('/add_to_cart_error/<product_id>', methods=['GET', 'POST'])
def add_to_cart_error(product_id):
    return render_template("add_to_cart_error.html", product_id=product_id)


if __name__ == '__main__':
    main()
