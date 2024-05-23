from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.user import RegisterForm, LoginForm
from forms.event import EventsForm
from data.events import Events
from data.users import User
from data.students import Students
from data.super_admins import super_admins_ids
from data import db_session, products_api

# import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

RATING_POINTS = {1: 1, 2: 5, 3: 20, 4: 100, 5: 1000}


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
@login_required
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
def register():
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
    # TODO верификация аккаунта через админку
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and not user.verified:
            return render_template("need_registration.html", title="Ваш аккаунт не верифицирован!")
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
@login_required
def add_event():
    form = EventsForm()
    # TODO выбор учеников из списка
    #  для начала, ссылка на список учеников
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        events = Events()
        events.event_name = form.event_name.data
        events.event_date = form.event_date.data
        events.value = form.value.data
        events.ids = f"[{form.ids.data}]"
        events.annotation = form.annotation.data
        current_user.events.append(events)
        db_sess.merge(events)
        db_sess.commit()
        return redirect('/')
    return render_template('events.html', title='Новое событие', form=form)


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
            form.ids.data = str(events.ids)[1:-1]
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
            events.ids = f"[{form.ids.data}]"
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
@login_required
def product_page(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Events).filter((Events.id == id)).first()
    students = []
    for i in eval(event.ids):
        student = db_sess.query(Students).filter((Students.id == i)).first()
        students.append(student)
    return render_template("event.html", item=event, title="Просмотр карточки события", students=students)


@app.route('/view_students', methods=['GET', 'POST'])
@login_required
def view_students():
    args = []
    db_sess = db_session.create_session()
    if request.method == 'POST':
        class_num = request.form.get('class_num')
        class_letter = request.form.get('class_letter')
        campus = request.form.get('campus')
        #redirect(f"/show_students?campus={campus}&class_num={class_num}&class_letter={class_letter}")
        if campus != "Все":
            args.append(Students.campus == campus)
        if class_num != "Все" and class_num != "":
            args.append(Students.class_num == class_num)
        if class_letter != "Все" and class_letter != "":
            args.append(Students.class_letter == class_letter)
        print(class_num)
    students = db_sess.query(Students).filter(*args)
    return render_template("students.html", title="Просмотр учеников", students=students)


@app.route('/update_rating', methods=['GET', 'POST'])
@login_required
def update_rating():
    db_sess = db_session.create_session()
    students = db_sess.query(Students).all()
    for student in students:
        student.rating_points = 0

    events = db_sess.query(Events).all()

    for event in events:
        for student_id in eval(event.ids):
            student = db_sess.query(Students).filter(Students.id == int(student_id)).first()
            student.rating_points += RATING_POINTS[int(event.value)]

    db_sess.commit()
    return redirect("/view_students")


@app.route("/student_card/<int:student_id>")
@login_required
def student_card(student_id):
    db_sess = db_session.create_session()
    student = db_sess.query(Students).filter(Students.id == int(student_id)).first()
    if student.id == 1:
        student.name = 'Фисунов Андрей Павлович'
        student.class_letter = 'Л'
        db_sess.commit()
    return render_template("student_card.html", student=student)
    # TODO расчет места в рейтинге


@app.route('/support', methods=['GET', 'POST'])
def support():
    return render_template("support.html")


if __name__ == '__main__':
    main()
