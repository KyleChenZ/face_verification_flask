from flask import Flask, Blueprint, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from resources.user import User, add_admin, add_user
from resources.face import Face, FaceList
from resources.face_verification import FaceVerification

from flask_login import LoginManager 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
#app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'face'  # could do app.config['JWT_SECRET_KEY'] if we prefer
api = Api(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models.user import UserModel

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return UserModel.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    # uncomment below line to add admin account at the begining. feel free to use a custom username and password and name
    add_admin({'username': 'admin','password': 'admin', 'name': 'admin'}) 

jwt = JWTManager(app)

"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below.
"""

'''
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):  # Remember identity is what we define when creating the access token
    if identity == 1:   # instead of hard-coding, we should read from a config file or database to get a list of admins instead
        return {'is_admin': True}
    return {'is_admin': False}
'''

# blueprint for auth routes in our app
from routes.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from routes.main import main as main_blueprint
app.register_blueprint(main_blueprint)

api.add_resource(Face, '/face', '/face/<string:id>')
api.add_resource(FaceList, '/faces')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(FaceVerification,'/verify_face')

if __name__ == '__main__':
    db.init_app(app)
    app.run(host='0.0.0.0',port=5000, debug=True)
