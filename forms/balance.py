from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import DataRequired


class AddBalanceForm(FlaskForm):
    amount = IntegerField("Сумма пополнения, уе", validators=[DataRequired()])
    submit = SubmitField('Применить')


class CheckOperation(FlaskForm):
    hash = StringField("Ваш код", validators=[DataRequired()])
    submit = SubmitField('Применить')
