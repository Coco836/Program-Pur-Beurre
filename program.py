# -*- coding : utf8 -*-

import mysql.connector
import requests

class OpenFoodFactsApi:
    """docstring for OpenFoodFactsApi."""

    def __init__(self):
        self.pur_beurre_db = DataBase()

    def fetch_categories_data_api(self):
        # Recover data from Open Food Facts URL API with request get.
        response = requests.get('https://fr.openfoodfacts.org/categories.json')
        # Save the json data in a variable.
        json_data_file = response.json()
        # Get only the data needed: data besides the one in the "tags" list are irrelevant here.
        data_tags = json_data_file.get('tags')
        # Select only the name of each category (no need for other data).
        category_data = [
                        element.get('name', 'None') for element in data_tags
                        if "🍩" not in element.get('name', 'None')
                        ]
        return category_data

    def fetch_products_data_api(self):
        category_data = self.fetch_categories_data_api()

        url_categories = []
        list_product_elements = []
        for name_cat in range(0, 20):
            url_categories.append(f'https://fr.openfoodfacts.org/categorie/{category_data[name_cat]}.json')
            response = requests.get(url_categories[name_cat])
            json_data_file = response.json()
            # Get only the data needed: data besides the one in the "tags" list are irrelevant here.
            data_products = json_data_file.get('products')
            product_informations = ['product_name', 'ingredients_text_debug', 'url', 'nutrition_grade_fr']
            product_elements = {}
            for i in product_informations:
                get_product_elements = [element.get(i, 'None') for element in data_products]
                product_elements.update({i : get_product_elements})
            list_product_elements.append(product_elements)
        return list_product_elements


class Category:
    """docstring for Category."""

    def __init__(self):
        self.api = OpenFoodFactsApi()
        self.pur_beurre_db = DataBase()

    def get_categories(self):
        category_data = self.api.fetch_categories_data_api()

        limit_nb_category = 0
        while limit_nb_category < 20:
            sql = "INSERT INTO category (name) VALUES (%s)"
            values = [category_data[limit_nb_category]]
            self.pur_beurre_db.insert_into_database(sql, values)
            limit_nb_category += 1
        self.pur_beurre_db.close_database()

    def save(self):
        pass


class Product:
    """docstring for Product."""

    def __init__(self):
        self.api = OpenFoodFactsApi()
        self.pur_beurre_db = DataBase()

    def get_products(self):
        list_product_elements = self.api.fetch_products_data_api()
        sql = "INSERT INTO product (name, description, url, nutrition_grade, id_category) VALUES (%s, %s, %s, %s, %s)"
        id_category = 0
        for dict in range(0, 20):
            id_category +=1
            for prod in range(0, 20):
                values = [
                list_product_elements[dict]['product_name'][prod],
                list_product_elements[dict]['ingredients_text_debug'][prod],
                list_product_elements[dict]['url'][prod],
                list_product_elements[dict]['nutrition_grade_fr'][prod],
                id_category
                ]
                print(values)
                self.pur_beurre_db.insert_into_database(sql, values)
        self.pur_beurre_db.close_database()


    def save(self):
        pass


class DataBase:
    """docstring for DataBase."""

    def __init__(self):
        # Connection to database pur_beurre with parameters
        self.my_data_base = mysql.connector.connect(host="localhost",
                            user="colette", passwd="", database="pur_beurre")


    def create_database_sql(self):
        "Script SQL"
        pass

    def insert_into_database(self, sql, values):
        #  Cursor: allows Python code to execute MySQL command in a database session.
        self.mycursor = self.my_data_base.cursor()
        # Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
        self.mycursor.execute(sql, values)
        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()
        # Rowcount: indicates number of rows affected.
        print(self.mycursor.rowcount, "was inserted.")

    def close_database(self):
        # Closing the connection
        self.my_data_base.close()


class Shop:
    """docstring for Shop."""

    def __init__(self):
        self.api = OpenFoodFactsApi()

    def get_shop_data(self):
        pass

    def save(self):
        pass

api = OpenFoodFactsApi()
category = Category()
product = Product()
shop = Shop()
pur_beurre_db = DataBase()
# api.fetch_products_data_api()
category.get_categories()
product.get_products()
