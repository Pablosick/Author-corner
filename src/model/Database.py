from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=False)
    avatar = db.Column(db.LargeBinary())
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"users {self.id}"


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    text = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(15), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
