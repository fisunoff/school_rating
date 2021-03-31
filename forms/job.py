import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    team_leader = IntegerField("ID ответственного", validators=[DataRequired()])
    job = StringField("Содержание работы", validators=[DataRequired()])
    work_size = IntegerField("Кол-во рабочих часов", validators=[DataRequired()])
    collaborators = StringField("Напарники", validators=[DataRequired()])
    start_date = DateTimeField("Время начала", default=datetime.datetime.now())
    end_date = DateTimeField("Время окончания")
    is_finished = BooleanField("Закончена?")
    submit = SubmitField('Применить')
