from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateTimeField, FileField
from wtforms.validators import DataRequired


class ProductsForm(FlaskForm):
    title = StringField("Наименование", validators=[DataRequired()])
    quantity = IntegerField("Количество товара на складе", validators=[DataRequired()])
    price = IntegerField("Цена", validators=[DataRequired()])
    description = StringField("Описание", validators=[DataRequired()])
    category = StringField("Категория")
    photo = FileField("Фото товара")
    submit = SubmitField('Применить')