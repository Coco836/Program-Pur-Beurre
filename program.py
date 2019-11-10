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
        category_data = [element.get('name', 'None') for element in data_tags if "🍩" not in element.get('name', 'None')]

        limit_nb_category = 0
        while limit_nb_category < 20:
            #  Cursor: allows Python code to execute MySQL command in a database session.
            self.mycursor = self.my_data_base.cursor()
            sql = "INSERT INTO category (name) VALUES (%s)"
            values = [category_data[limit_nb_category]]
            # Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
            self.mycursor.execute(sql, values)

            # Commit: save data in data base table before closing connection.
            self.my_data_base.commit()

            # Rowcount: indicates number of rows affected.
            print(self.mycursor.rowcount, "was inserted.")

            limit_nb_category += 1
        # Closing the connection
        self.my_data_base.close()


    def get_products_data(self, response):
        # Save the json data in a variable.
        json_data_file = response.json()
        # Get only the data needed: data besides the one in the "tags" list are irrelevant here.
        data_products = json_data_file.get('products')
        # Select only the name of each category (no need for other data).
        # product_name = [element.get('product_name', 'None') for element in data_products]
        # product_description = [element.get('ingredients_text_debug', 'None') for element in data_products]
        # product_url = [element.get('url', 'None') for element in data_products]
        # product_grade = [element.get('nutrition_grade_fr', 'None') for element in data_products]
        # print("NOM PRODUIT = ", product_name[18])
        # print("DESCRIPTION PRODUIT = ", product_description[18])
        # print("PRODUIT URL = ", product_url[18])
        # print("NOTE NUTRITION PRODUIT = ", product_grade[18])

        product_elements = {}
        product_informations = ['product_name', 'ingredients_text_debug', 'url', 'nutrition_grade_fr']
        for i in product_informations:
            get_product_elements = [element.get(i, 'None') for element in data_products]
            product_elements.update({i : get_product_elements})
        print(product_elements)
        return product_elements

        # 'product_name', 'ingredients_text_debug', 'url', 'nutrition_grade_fr'

    def insert_into_database(self):
        # Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
        self.mycursor.execute(sql, values)

        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()

        # Rowcount: indicates number of rows affected.
        print(self.mycursor.rowcount, "was inserted.")


    def fill_data_product(self):
        response = requests.get('https://fr.openfoodfacts.org/categorie/Aliments%20et%20boissons%20%C3%A0%20base%20de%20v%C3%A9g%C3%A9taux.json')
        self.get_products_data(response)

    def get_shop_data(self, arg):
        pass

    # def creation_data_base_sql(self, arg):
    #     pass

pur_beurre_db = OpenFoodFactsApi()
# pur_beurre_db.get_categories_data()
pur_beurre_db.fill_data_product()
