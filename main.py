from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_,and_, func, DateTime
from sqlalchemy.sql import func

import datetime
import sqlite3
from sqlitemodel import Model, Database
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import json
from user_details_class import user_details
import csv
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Mattisthebestprogrammerintheworld!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_database.db'

Bootstrap(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class UserDetails(db.Model):
    __tablename__ = "UserDetails"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    favourite_colour = db.Column(db.String(10))
    favourite_food = db.Column(db.String(10))
    favourite_sport = db.Column(db.String(10))


class Friendships(db.Model):
    __tablename__ = "Friendships"
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    friend = db.Column(db.Integer)

class ChatLog(db.Model):
	__tablename__ = "ChatLog"
	id = db.Column(db.Integer, primary_key=True)
	sender_id = db.Column(db.Integer)
	reciever_id = db.Column(db.Integer)
	message_text = db.Column(db.String(160))
	date_sent = db.Column(DateTime(timezone=False), server_default=func.now())
	

def get_user_details_list(list_of_ids):
    details_list = []
    for x in list_of_ids:
        userTable = User.query.filter_by(id=x).first()
        userDetails = UserDetails.query.filter_by(user_id=x).first()
        details_list.append(userTable.first_name)
        details_list.append(userTable.username)
        details_list.append(userDetails.favourite_colour)
        details_list.append(userDetails.favourite_food)
        details_list.append(userDetails.favourite_sport)
    return details_list


def get_user_prefrences(id):
    current_userDetails = UserDetails.query.filter_by(user_id=id).first()
    return current_userDetails


def appendIfNotIn(list, entry):
    if entry not in list and entry != current_user.get_id():
        list.append(entry)


def find_friends(current_user_id):
    userDetails = get_user_prefrences(current_user_id)
    friendList = []

    for x in range(0, 8):
        similar_colour = UserDetails.query.filter_by(
            favourite_colour=userDetails.favourite_colour).order_by(
                func.random()).first()
        similar_food = UserDetails.query.filter_by(
            favourite_food=userDetails.favourite_food).order_by(
                func.random()).first()
        similar_sport = UserDetails.query.filter_by(
            favourite_sport=userDetails.favourite_sport).order_by(
                func.random()).first()

        appendIfNotIn(friendList, similar_colour.user_id)
        appendIfNotIn(friendList, similar_food.user_id)
        appendIfNotIn(friendList, similar_sport.user_id)

    return get_user_details_list(friendList), friendList


def add_friend(friend_id):
    new_user = Friendships(userId=current_user.get_id(), friend=friend_id)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('dashboard'))


def get_friend_list(user_id):
    friend_list = []
    friendships = Friendships.query.filter_by(userId=user_id).all()
    for user in friendships:
        appendIfNotIn(friend_list, user.friend)

    return friend_list, get_user_details_list(friend_list)


def remove_friend(user_id, friend_id):
    Friendships.query.filter_by(userId=user_id, friend=friend_id).delete()
    db.session.commit()


def return_search_results_friends(search_entry):
    friend_search = User.query.filter(
        or_(func.lower(User.username) == func.lower(search_entry),
            func.lower(User.first_name) == func.lower(search_entry))).all()
    results_list = []
    for results in friend_search:
        appendIfNotIn(results_list, results.id)
    return get_user_details_list(results_list), results_list

def get_chatlog(senderId, recieverId):
	sent_messages = []
	received_messages = []
	all_chats = ChatLog.query.where(
		(ChatLog.sender_id==int(senderId)) & (ChatLog.reciever_id==int(recieverId)) | (ChatLog.sender_id==int(recieverId)) & (ChatLog.reciever_id==int(senderId)) ).all()
	for message in all_chats:
		print(message.sender_id,message.reciever_id)
		if message.sender_id == int(senderId) and message.reciever_id == int(recieverId):
			sent_messages.append(message.message_text)
			
		if message.sender_id == int(recieverId) and message.reciever_id == int(senderId):
			received_messages.append(message.message_text)
			
	print("messages",sent_messages, received_messages)
	return sent_messages , received_messages, all_chats

def send_message(sender_id, reciever_id,message):
	print(sender_id, reciever_id,message)
	new_message = ChatLog(sender_id=sender_id,reciever_id=reciever_id,message_text=message, date_sent=func.now())
	print(new_message)
	db.session.add(new_message)
	db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('',
                           validators=[InputRequired(),
                                       Length(min=4, max=16)])
    password = PasswordField(
        '', validators=[InputRequired(),
                        Length(min=8, max=80)])
    remember = BooleanField('Remember me')


class RegisterForm(FlaskForm):
    first_name = StringField(
        '', validators=[InputRequired(),
                        Length(min=4, max=16)])
    email = StringField('',
                        validators=[
                            InputRequired(),
                            Email(message="invalid email"),
                            Length(max=50)
                        ])
    username = StringField('',
                           validators=[InputRequired(),
                                       Length(min=4, max=16)])
    password = PasswordField(
        '', validators=[InputRequired(),
                        Length(min=8, max=80)])
class SendMessage(FlaskForm):
	message_input = StringField('', validators=[InputRequired(),Length(min=1,max=160)])

colour_options = [
    "Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"
]
food_options = [
    "Chips", "Doughnuts", "Ice Cream", "Chicken Nuggets", "Pizza", "Burgers",
    "Steak", "Sausages"
]
sport_options = [
    "Football", "Rugby", "Cricket", "Badminton", "Cycling", "Tennis",
    "Basketball"
]


class SetupForm(FlaskForm):
    favourite_colour = SelectField(choices=colour_options)
    favourite_food = SelectField(choices=food_options)
    favourite_sport = SelectField(choices=sport_options)

def populate_db():
    colour_options = [
        "Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"
    ]
    food_options = [
        "Chips", "Doughnuts", "Ice Cream", "Chicken Nuggets", "Pizza",
        "Burgers", "Steak", "Sausages"
    ]
    sport_options = [
        "Football", "Rugby", "Cricket", "Badminton", "Cycling", "Tennis",
        "Basketball"
    ]

    for i in range(0, 1000):
        hashed_password = generate_password_hash(read_common_names(i),
                                                 method='sha256')
        user_email = read_common_names(i) + '@email.com'
        new_username = read_common_names(i) + str(random.randint(1, 100))
        new_user = User(first_name=read_common_names(i),
                        username=new_username,
                        email=user_email,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        user_prefrences = UserDetails(
            user_id=i + 1,
            favourite_colour=colour_options[random.randint(
                0,
                len(colour_options) - 1)],
            favourite_food=food_options[random.randint(0,
                                                       len(food_options) - 1)],
            favourite_sport=sport_options[random.randint(
                0,
                len(sport_options) - 1)])
        db.session.add(user_prefrences)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('login'))


@app.route('/populate/', methods=['GET', 'POST'])
def populate_table():
    populate_db()
    return "done"


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    elif form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid Username or password</h1>'

    return render_template('login.html', form=form)


@app.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data,
                                                 method='sha256')
        new_user = User(first_name=form.first_name.data,
                        username=form.username.data,
                        email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login()

        return redirect(url_for('user_setup'))

    return render_template('sign-up.html', form=form)


@app.route('/sign-up/setup', methods=['GET', 'POST'])
@login_required
def user_setup():
    form = SetupForm()
    if form.validate_on_submit():
        user_prefrences = UserDetails(
            user_id=current_user.get_id(),
            favourite_colour=form.favourite_colour.data,
            favourite_food=form.favourite_food.data,
            favourite_sport=form.favourite_sport.data)
        db.session.add(user_prefrences)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('user-setup.html',
                           name=current_user.username,
                           first_name=current_user.first_name,
                           form=form)
@login_required
@app.route('/chat/', methods=['GET', 'POST'])
@app.route('/chat/<friend_id>', methods=['GET', 'POST'])
def chat(friend_id=None):
	user_id = current_user.get_id()
	print(user_id)
	form = SendMessage()
	friend_details = None
	friend_name = None
	all_chats=None
	sent_messages, received_messages = [], []
	friend_list, friend_details_list = get_friend_list(current_user.get_id())
	if friend_id:
		friend_details = User.query.filter_by(id=friend_id).first()
		friend_name=friend_details.first_name
		if form.validate_on_submit():
			send_message(sender_id=current_user.get_id(), reciever_id=friend_id,message=form.message_input.data)
		sent_messages, received_messages,all_chats = get_chatlog(current_user.get_id(), friend_id)
		
	

	return render_template('chat.html',user_id=user_id,all_chats=all_chats, form=form,sent_messages=sent_messages,received_messages=received_messages,friend_name=friend_name,friend_id=friend_id, friend_list=friend_list, friend_details_list=friend_details_list, first_name=current_user.first_name)




@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
    search_results = None
    search_ids = []
    search_query = "Search for new friends:"
    if request.method == 'POST':
        friend_to_remove = request.form.get("remove-friend")
        if friend_to_remove:
            remove_friend(current_user.get_id(), friend_to_remove)

        friend_id = request.form.get("friend-id-input")
        if friend_id:
            add_friend(friend_id)
        search_query = request.form.get("friend-search")
        if search_query:
            search_results, search_ids = return_search_results_friends(
                search_query)
    similarFriends, id_similar_list = find_friends(current_user.get_id())
    friend_list, friend_details_list = get_friend_list(current_user.get_id())

    return render_template('dashboard.html',
							search_query=str(search_query),
							search_ids=search_ids,
							search_results=search_results,
							friend_details_list=friend_details_list,
							friend_list=friend_list,
							id_similar_list=id_similar_list,
							similarFriends=similarFriends,
							username=current_user.username,
							first_name=current_user.first_name)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/preferences/', methods=['GET', 'POST'])
@login_required
def preferences():

    return render_template('preferences.html', name=current_user.username)


app.run(host='0.0.0.0', port=81, debug=True)
