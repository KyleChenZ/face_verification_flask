from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

def add_user(data):
    if UserModel.find_by_username(data['username']):
        return {"message": "A user with that username already exists"}, 400
    else:
        data['password'] = generate_password_hash(data['password'], method='sha256')
        user = UserModel(**data)
        user.save_to_db()

def add_admin(data):
    if UserModel.find_by_username(data['username']):
        return {"message": "A user with that username already exists"}, 400
    else:
        data['role'] = 'admin'
        data['password'] = generate_password_hash(data['password'], method='sha256')
        user = UserModel(**data)
        user.save_to_db()

class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
