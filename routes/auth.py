# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login.utils import encode_cookie
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.user import UserModel as User
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, create_access_token, create_refresh_token
from db import db

auth = Blueprint('auth', __name__, template_folder='../templates')

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password): 
        print(user and check_password_hash(user.password, password), user.password == password)
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)

    resp = redirect(url_for('main.profile'),302)
    

    access_token = create_access_token(identity = user.id)
    refresh_token = create_refresh_token(identity = user.id)

    resp.headers['Authorization'] = 'Bearer {}'.format(access_token)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():

    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')
    role = 'user'

    user = User.query.filter_by(username=username).first() # if this returns a user, then the username already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again  
        flash('Username address already exists')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(username=username, name=name, password=generate_password_hash(password, method='sha256'), role=role)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))