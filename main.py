from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import email_validator
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from sqlitemodel import Model, Database

import json
from user_details_class import user_details
import csv
import random

database = sqlite3.connect("database.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Edisthebestprogrammerintheworld!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'C:\\Users\\edwar\\Desktop\\Facebook_flask\\Facebook_Flask\\database.db'
Bootstrap(app)

db = SQLAlchemy(app)
db.create_all()
# db = sqlite3.connect('users.db')
user_file = "users.json"


def write_json(new_data,array_name, filename=user_file):
		global  last_id
		with open(filename,'r+') as file:
			
			file_data = json.load(file)
			
			file_data[array_name].append(new_data)
			# Sets file's current position at offset.
			file.seek(0)
			# convert back to json.
			json.dump(file_data, file, indent = 4)

def get_next_id():
	user_file = "users.json"
	last_id = 0
	
	with open(user_file,'r+') as file:
			
		file_data = json.load(file)
		
		for item in file_data["user_details"]:
			last_id = item['id'] 
					
	return last_id +1

def load_json(value_name, file=user_file):
	last_id = 0
	values_in_name = []
	with open(file,'r+') as file:
			
		file_data = json.load(file)
		
		for item in file_data["user_details"]:
			values_in_name.append(item[value_name] )
					
	return values_in_name

def populate():

	colour_options = ["Red","Orange","Yellow","Green","Blue","Indigo","Violet"]
	food_options = ["Chips","Doughnuts","Ice Cream","Chicken Nuggets","Pizza","Burgers","Steak","Sausages"]
	sport_options = ["Football","Rugby","Cricket","Badminton","Cycling","Tennis","Basketball"]
	
	next_id = get_next_id()
	
	def read_common_names(increment):
		with open('common_names.csv', 'r') as names:
			rows = list(names)
			return rows[increment].rstrip('\n')

	for i in range (0,1133):
		next_id = get_next_id()
		user_details.name = read_common_names(i).lower()
		user_details.age = random.randint(10,50)
		user_details.favourite_colour = colour_options[random.randint(0,len(colour_options)-1)]
		user_details.favourite_food = food_options[random.randint(0,len(food_options)-1)]
		user_details.favourite_sport = sport_options[random.randint(0,len(sport_options)-1)]
		
		
		dictionary = {
			"id":next_id,
			"name": user_details.name,
			"age": user_details.age,
			"favourite_colour":user_details.favourite_colour,
			"favourite_food":user_details.favourite_food,
			"favourite_sport":user_details.favourite_sport,
	
	
		}

		write_json(dictionary, array_name="user_details",filename="users.json")
			

def get_user_input():
	
	next_id = get_next_id()
	
	user_details.name = request.form["user_name"].lower()
	user_details.age = int(request.form["user_age"])
	user_details.favourite_colour = request.form["favourite_colour"]
	user_details.favourite_food = request.form["favourite_food"]
	user_details.favourite_sport = request.form["favourite_sport"]

	# if user_details.name in load_json("name"):
	# 	if user_details.age in load_json("age"):
	# 		if user_details.favourite_colour in load_json("favourite_colour"):
	# 			if user_details.favourite_food in load_json("favourite_food"):
	# 				if user_details.favourite_sport in load_json("favourite_sport"):
	# 					duplicate = True
	# 					# If duplicate return duplicate
					
		

	dictionary = {
	"id":next_id,
	"name": user_details.name,
	"age": user_details.age,
	"favourite_colour":user_details.favourite_colour,
	"favourite_food":user_details.favourite_food,
	"favourite_sport":user_details.favourite_sport,
	
	
	}

	write_json(dictionary, array_name="user_details",filename="users.json")


def filter_by():

	user_details.name = request.form["user_name"].lower()
	user_details.age = int(request.form["user_age"])
	user_details.favourite_colour = request.form["favourite_colour"]
	user_details.favourite_food = request.form["favourite_food"]
	user_details.favourite_sport = request.form["favourite_sport"]
	
	
	filter_options= ["name","age","favourite_colour","favourite_food","favourite_sport"]
	
	
	with open("users.json","r+") as file:
		
		file_data = json.load(file)
		
		name_match = []
		age_match = []
		colour_match = []
		food_match = []
		sport_match = []
		
		for selection in filter_options:
			for item in file_data["user_details"]:
				if selection == "name":
					if user_details.name == item["name"]:
						name_match.append(item["id"])
				elif selection == "age":
					if user_details.age == item["age"]:
						age_match.append(item["id"])
						
				elif selection == "favourite_colour":
					if user_details.favourite_colour == item["favourite_colour"]:
						colour_match.append(item["id"])
						
				elif selection == "favourite_food":
					if user_details.favourite_food == item["favourite_food"]:
						food_match.append(item["id"])
						
				elif selection == "favourite_sport":
					if user_details.favourite_sport == item["favourite_sport"]:
						sport_match.append(item["id"])
		this_id = get_next_id()-1
		dictionary = {
			"id":this_id,
			"same_name" : name_match,
			"same_age" : age_match,
			"same_colour" : colour_match,
			"same_food" : food_match,
			"same_sport" : sport_match,
			
		}
	file.close()
	write_json(dictionary, array_name="likeness",filename="likeness.json")
					

def most_like(user_id):
	with open("likeness.json","r+") as file:

		friend_list = []
		
		file_data = json.load(file)

		for item in file_data["likeness"]:
			if item["id"] == user_id:
				# if same age and same colour
				
				for x in range(0,len(item["same_age"])):
					if item["same_age"][x] in item["same_colour"] and item["same_age"][x] not in friend_list:
						friend_list.append(item["same_age"][x])
						break
				# if same food and sport
				for x in range(0,len(item["same_food"])):
					if item["same_food"][x] in item["same_sport"] and item["same_food"][x] not in friend_list:
						friend_list.append(item["same_food"][x])
						break
				# same age and sport
				for x in range(0,len(item["same_age"])):
					if item["same_age"][x] in item["same_sport"] and item["same_age"][x] not in friend_list:
						friend_list.append(item["same_age"][x])
						break
				# same sport and colour
				for x in range(0,len(item["same_sport"])):
					if item["same_sport"][x] in item["same_colour"] and item["same_sport"][x] not in friend_list:
						friend_list.append(item["same_sport"][x])
						break

	print("friend list is",friend_list)
	return friend_list

def get_friend_details_for_html(friend_list):
	aggregate_list = []
	
	with open("users.json","r") as file:
		file_data = json.load(file)
	
	for id in friend_list:
		for item in file_data["user_details"]:
			if id == item["id"]:
				aggregate_list.append(item["id"])
				aggregate_list.append(item["name"])
				aggregate_list.append(item["age"])
				aggregate_list.append(item["favourite_colour"])
				aggregate_list.append(item["favourite_food"])
				aggregate_list.append(item["favourite_sport"])

	print(aggregate_list)

	return aggregate_list
			
class User(db.Model):
	id = db.Column(db.Integer, primary_key= True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4,max=16)])
	password = PasswordField('password', validators=[InputRequired(),Length(min=8,max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message="invalid email"),Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4,max=16)])
	password = PasswordField('password', validators=[InputRequired(),Length(min=8,max=80)])



@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		# similar_person()
		# filter_by_characteristics(request.form["filter_select"])
		pass
		

		
	colour_options = ["Red","Orange","Yellow","Green","Blue","Indigo","Violet"]
	food_options = ["Chips","Doughnuts","Ice Cream","Chicken Nuggets","Pizza","Burgers","Steak","Sausages"]
	sport_options = ["Football","Rugby","Cricket","Badminton","Cycling","Tennis","Basketball"]
	filter_options= ["name","age","favourite_colour","favourite_food","favourite_sport"]
	return render_template("index.html" ,filter_options=filter_options,colour_options=colour_options, food_options=food_options, sport_options=sport_options)


@app.route('/friends-match/',methods=['GET','POST'])
def match_results():
	aggregate_list = []
	if request.method == 'POST':
		get_user_input()
		this_id = get_next_id()-1
		filter_by()
		aggregate_list = get_friend_details_for_html(most_like(this_id))

	friend_card_prefixes = ["User ID:  ","Name:  ","Age:  ","Favourite Colour:  ", "Favourite Food:  ","Favourite Sport:  "]
	return render_template('friends-match.html',friend_card_prefixes=friend_card_prefixes ,user_details=user_details,aggregate_list=aggregate_list)

@app.route('/populate/',methods=['GET','POST'])
def populate_table():
	if request.method == 'POST':
		
		populate()

	return render_template('index.html',user_details=user_details)

@app.route('/sign-up/',methods=['GET','POST'])
def sign_up():
	form = RegisterForm()

	if form.validate_on_submit():
		pass
		
	return render_template('sign-up.html',form=form)

@app.route('/login/', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		return '<h1>' + form.username.data + '' + form.password.data + '</h1>'
	
	return render_template('login.html',form=form)

app.run(host='0.0.0.0', port=81)
