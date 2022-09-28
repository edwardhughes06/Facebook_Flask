from flask import Flask, render_template, request
from main import *
import json


user_file = 'users.json'

class user_details:
		def __init__(self, name, age, favourite_colour, favourite_food, favourite_sport):
			self.name = name
			self.age = age
			self.favourite_colour = favourite_colour
			self.favourite_food = favourite_food
			self.favourite_sport = favourite_sport

	# user_details.name = str_input("Enter your name: ", 1)
	# user_details.age = int_input("Enter your age: ", 1)
	# user_details.favourite_colour = str_input("Enter your favourite colour: ", 1)
	# user_details.favourite_food = str_input("Enter your favourite food: ", 1)
	# user_details.favourite_sport = str_input("Enter your favourite sport: ", 1)





def write_json(new_data, filename=user_file):
		global  last_id
		with open(filename,'r+') as file:
			
			file_data = json.load(file)
			
			file_data["user_details"].append(new_data)
			# Sets file's current position at offset.
			file.seek(0)
			# convert back to json.
			json.dump(file_data, file, indent = 4)



while True:
	last_id = 0
	with open(user_file,'r+') as file:
			
			file_data = json.load(file)
			
			for item in file_data["user_details"]:
				print(item['id'])
				last_id = item['id'] 
					
	print("last id:",last_id)
	next_id = last_id +1
	
	def str_input(input_string, min_value):
		while True:
			try:
				string = str(input(input_string))
				if len(string) > min_value:
					return string
					break
			except:
				print("Input must be string and/or greater than",min_value)
				

	def int_input(input_string, min_value):
		while True:
			try:
				integer = int(input(input_string))
				if integer > min_value:
					return integer
					break
			except:
				print("Input must be integer and/or greater than",min_value)
				
	
	
	
	
	
	
	
	dictionary = {
		"id":next_id,
		"name": user_details.name,
		"age": user_details.age,
		"favourite_colour":user_details.favourite_colour,
		"favourite_food":user_details.favourite_food,
		"favourite_sport":user_details.favourite_sport,
		
		
	}
	
	write_json(dictionary)