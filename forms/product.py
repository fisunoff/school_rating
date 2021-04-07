from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import DataRequired


class ProductsForm(FlaskForm):
    title = StringField("Наименование", validators=[DataRequired()])
    quantity = IntegerField("Количество товара на складе", validators=[DataRequired()])
    price = StringField("Цена", validators=[DataRequired()])
    description = IntegerField("Описание", validators=[DataRequired()])
    category = StringField("Категория")
    submit = SubmitField('Применить')