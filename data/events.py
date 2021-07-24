import datetime
import sqlalchemy
from sqlalchemy import orm

from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Events(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    event_name = sqlalchemy.Column(sqlalchemy.String)
    event_date = sqlalchemy.Column(sqlalchemy.Date, default="2020-10-10")
    event_add_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relationship('User', foreign_keys="Events.author_id", backref="events")
    value = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    ids = sqlalchemy.Column(sqlalchemy.String, default="[]")
    annotation = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'<Event> {self.id} {self.event_name} {self.author}'
