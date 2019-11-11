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
            sql = "INSERT INTO category (name) VALUES (%s)"
            values = [category_data[limit_nb_category]]
            self.insert_into_database(sql, values)
            limit_nb_category += 1
        # Closing the connection
        self.my_data_base.close()


    def get_products_data(self):
        # Recover data from Open Food Facts URL API with request get.
        response = requests.get('https://fr.openfoodfacts.org/categories.json')
        # Save the json data in a variable.
        json_data_file = response.json()
        # Get only the data needed: data besides the one in the "tags" list are irrelevant here.
        data_tags = json_data_file.get('tags')
        category_data = [element.get('url', 'None') for element in data_tags]

        cat = []
        for a in range(0, 19):
            cat.append(category_data[a] + '.json')
            resp = requests.get(cat[a])
            js = resp.json()
            # Get only the data needed: data besides the one in the "tags" list are irrelevant here.
            data_products = js.get('products')
            list_product_elements = []
            product_elements = {}
            product_informations = ['product_name', 'ingredients_text_debug', 'url', 'nutrition_grade_fr']
            for i in product_informations:
                get_product_elements = [element.get(i, 'None') for element in data_products]
                product_elements.update({i : get_product_elements})
            list_product_elements.append(product_elements)
            print(list_product_elements)


    def insert_into_database(self, sql, values):
        #  Cursor: allows Python code to execute MySQL command in a database session.
        self.mycursor = self.my_data_base.cursor()
        # Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
        self.mycursor.execute(sql, values)
        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()
        # Rowcount: indicates number of rows affected.
        print(self.mycursor.rowcount, "was inserted.")



    def get_shop_data(self, arg):
        pass

    # def creation_data_base_sql(self, arg):
    #     pass

pur_beurre_db = OpenFoodFactsApi()
# pur_beurre_db.get_categories_data()
pur_beurre_db.get_products_data()
