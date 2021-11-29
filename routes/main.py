# main.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.user import UserModel
from models.face import FaceModel
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

#from resources.user import User

main = Blueprint('main', __name__, template_folder='../templates')

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    print(current_user.role)
    if current_user.role == 'admin':
        users = UserModel.find_all()
        return render_template('face_list.html', name=current_user.name, users=users)
    else:
        user_data = UserModel.find_by_id(current_user.id).json()
        data = []
        #print(user_data)
        for f in user_data['faces']:
            data.append({'id':f['id'],'date_created':f['date_created']})
        count = len(data)
        #print(data)
        return render_template('face_list.html', name=current_user.name, data=data, count=count)
    
    #return render_template('profile.html', name=current_user.name)

@main.route('/face_id')
@login_required
def face_id():
    user = UserModel.find_by_id(current_user.id)
    allowed=False
    if len(user.json()['faces']) < 3:
        allowed=True
    return render_template('add_face_id.html', allowed=allowed)


@main.route('/face_verification')
@login_required
def face_verification():
    #user = UserModel.find_by_id(current_user.id)
    #allowed=False
    return render_template('face_verification.html', name=current_user.name)