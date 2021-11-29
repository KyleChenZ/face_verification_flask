from flask_login import UserMixin
from db import db
from datetime import datetime


class FaceModel(UserMixin, db.Model):
    __tablename__ = 'faces'

    id = db.Column(db.Integer, primary_key=True)
    face_vectors = db.Column(db.JSON)
    date_created = db.Column(db.DateTime, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel', foreign_keys='FaceModel.user_id')
    

    def __init__(self, face_vectors, user_id):
        self.face_vectors = face_vectors
        self.user_id = user_id
        self.date_created = datetime.now()

    def json(self):
        return {
            'id': self.id,
            'face_vectors': self.face_vectors,
            'user_id': self.user_id,
            'date_created': self.date_created.strftime("%m/%d/%Y, %H:%M:%S")
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id)
    
    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
