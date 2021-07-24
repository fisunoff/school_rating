from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateTimeField, FileField, DateField
from wtforms.validators import DataRequired


class EventsForm(FlaskForm):
    event_name = StringField("Наименование", validators=[DataRequired()])
    event_date = DateField("Дата проведения события")
    value = IntegerField("Значимость")
    ids = StringField("Id участников")
    annotation = StringField("Описание")
    submit = SubmitField('Применить')
