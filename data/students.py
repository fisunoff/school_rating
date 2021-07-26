import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Students(SqlAlchemyBase, UserMixin):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    class_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=5)
    campus = sqlalchemy.Column(sqlalchemy.CHAR, nullable=True, default='Т')
    class_letter = sqlalchemy.Column(sqlalchemy.CHAR, nullable=True)
    exp_amount = sqlalchemy.Column(sqlalchemy.Integer)
    rating_points = sqlalchemy.Column(sqlalchemy.Integer)
    rating_place = sqlalchemy.Column(sqlalchemy.Integer)
    role = sqlalchemy.Column(sqlalchemy.String)
    skin_id = sqlalchemy.Column(sqlalchemy.Integer)
    available_skins = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_visit = sqlalchemy.Column(sqlalchemy.DateTime)

    def __repr__(self):
        return f'{self.name}  {self.class_num}{self.class_letter}, корпус {self.campus}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_role(self):
        return self.role
