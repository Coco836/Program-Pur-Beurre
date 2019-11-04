# -*- coding : utf8 -*-

import mysql.connector
import requests

class OpenFoodFactsApi:
    """docstring for OpenFoodFactsApi."""

    def __init__(self):
        # Connection to databse pur_beurre with parameters
        self.my_data_base = mysql.connector.connect(host="localhost",
                            user="colette", passwd="", database="pur_beurre")

    def get_categories_data(self):
        # Recover data from Open Food Facts URL API with request get.
        response = requests.get('https://fr.openfoodfacts.org/categories.json')
        # Save the json data in a variable.
        json_data_file = response.json()
        # Get only the data needed: data besides the one in the "tags" list are irrelevant here.
        data_tags = json_data_file.get('tags')
        # Select only the name of each category (no need for other data).
        category_data = [(element.get('name', 'None'),) for element in data_tags if "🍩" not in element.get('name', 'None')]
        print(category_data)

        #  Cursor: allows Python code to execute MySQL command in a database session.
        self.mycursor = self.my_data_base.cursor()

        # Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
        self.mycursor.executemany("INSERT INTO category (name) VALUES (%s)", category_data)

        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()

        # Rowcount: indicates number of rows affected.
        print(self.mycursor.rowcount, "was inserted.")

        # Closing the connection
        self.my_data_base.close()

    def get_products_data(self, arg):
        pass

    def get_shop_data(self, arg):
        pass

    def save_result(self, arg):
        pass

    def creation_data_base_sql(self, arg):
        pass

pur_beurre_db = OpenFoodFactsApi()
pur_beurre_db.get_categories_data()
