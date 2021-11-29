from flask_login import UserMixin
from db import db
from datetime import datetime

class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    name = db.Column(db.String(80))
    role = db.Column(db.String(80))
    date_created = db.Column(db.DateTime, default=datetime.now())

    faces = db.relationship('FaceModel', lazy='dynamic')
    

    def __init__(self, username, password, name, role):
        self.username = username
        self.password = password
        self.name = name
        self.role = role
        self.date_created = datetime.now()

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'role': self.role,
            'faces': [face.json() for face in self.faces.all()],
            'date_created': self.date_created.strftime("%m/%d/%Y, %H:%M:%S")
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()