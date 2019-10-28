# -*- coding : utf8 -*-

import mysql.connector
import requests
# import json

# Recover data from Open Food Facts URL API with request get.
response = requests.get('https://fr.openfoodfacts.org/categories.json')
# Save the json data in a variable.
json_data_file = response.json()
# Get only the data needed: data besides the one in the "tags" list are irrelevant here.
data_tags = json_data_file.get('tags')
# Select only the name of each category (no need for other data).
category_data = [element.get('name', 'None') for element in data_tags]
print(category_data)

# Connection to databse pur_beurre with parameters
my_data_base = mysql.connector.connect(
  host="localhost",
  user="colette",
  passwd="",
  database="pur_beurre"
)

#  Cursor: allows Python code to execute MySQL command in a database session.
mycursor = my_data_base.cursor()

# Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
reference = (category_data)
mycursor.execute("INSERT INTO category (name) VALUES (%s)", reference)

# Commit: save data in data base table before closing connection.
my_data_base.commit()

# Rowcount: indicates number of rows affected.
# print(mycursor.rowcount, "was inserted.")

# Closing the connection
# my_data_base.close()
