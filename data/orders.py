import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    products = sqlalchemy.Column(sqlalchemy.String, default="{}")
    status = sqlalchemy.Column(sqlalchemy.String, default="{}")

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User', foreign_keys="Orders.user_id", backref="orders")

    def __repr__(self):
        return f'<Product> {self.id} {self.products} {self.status}'
