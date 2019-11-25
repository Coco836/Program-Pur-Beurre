# -*- coding : utf8 -*-

import mysql.connector
import requests

class OpenFoodFactsApi:
    """docstring for OpenFoodFactsApi."""

    def __init__(self):
        pass

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

    def fetch_products_data_api(self, myresult):
        id_category = myresult[0]
        category_name = myresult[1]
        url_categories = (f'https://fr.openfoodfacts.org/categorie/{category_name}.json')
        response = requests.get(url_categories)
        json_data_file = response.json()
        data_products = json_data_file.get('products')
        return data_products, id_category, category_name


class Category:
    """docstring for Category."""

    def __init__(self, id = None, name = ''):
        self.id = id
        self.name = name


    @classmethod
    def get_categories(cls, api, database):
        category_data = api.fetch_categories_data_api()

        for name in category_data[:20]:
            sql = "INSERT INTO category (name) VALUES (%s)"
            values = [name]
            database.execute(sql, values)

    def save(self):
        pass


class Product:
    """docstring for Product."""

    def __init__(self, id = None, name = '', description = '', shops = [],
                    substitute = '', categories = [], nutrition_grade = '',
                    url = ''):
        self.id = id
        self.name = name
        self.description = description
        self.shops = shops
        self.substitute = substitute
        self.categories = categories
        self.nutrition_grade = nutrition_grade

    @classmethod
    def get_products(cls, database, api):
        for id in range(1, 21):
            (data_products, id_category, category_name) = database.select_category(api, id)
            for data in range(0, 20):
                prod_name = [element.get('product_name') for element in data_products]
                prod_ingredients = [element.get('ingredients_text_fr') for element in data_products]
                prod_url = [element.get('url') for element in data_products]
                prod_nutriscore = [element.get('nutrition_grade_fr') for element in data_products]
                prod_data = [prod_name[data], prod_ingredients[data], prod_url[data], prod_nutriscore[data], id_category]
                sql = "INSERT INTO product (name, description, url, nutrition_grade, id_category) VALUES (%s, %s, %s, %s, %s)"
                values = prod_data
                database.execute(sql, values)


    def save(self):
        pass


class DataBase:
    """docstring for DataBase."""

    def __init__(self):
        # Connection to database pur_beurre with parameters
        self.my_data_base = mysql.connector.connect(host="localhost",
                            user="colette", passwd="", database="pur_beurre", buffered = True)
        #  Cursor: allows Python code to execute MySQL command in a database session.
        self.mycursor = self.my_data_base.cursor()


    def create_database_sql(self):
        "Script SQL"
        pass

    def execute(self, sql, values):
        # Execute: insert a recording the table category with request SQL INSERT INTO, from a list.
        self.mycursor.execute(sql, values)
        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()
        # Rowcount: indicates number of rows affected.
        print(self.mycursor.rowcount, "was inserted.")

    def select_category(self, api, id):
        id = id
        self.mycursor.execute("SELECT id, name FROM Category WHERE id = '%s'" % (id))
        myresult = self.mycursor.fetchone()
        (data_products, id_category, category_name) = api.fetch_products_data_api(myresult)
        return data_products, id_category, category_name

    def close_database(self):
        # Closing the connection
        self.my_data_base.close()


class Shop:
    """docstring for Shop."""

    def __init__(self, id = None, name = ''):
        self.id = id
        self.name = name

    # @classmethod
    def get_shop_data(cls, api, database):
        pass

    def save(self):
        pass

api = OpenFoodFactsApi()
database = DataBase()
category = Category()
product = Product()
# shop = Shop()
# shop = get_shop_data(api, database)
# api.fetch_products_data_api()
category.get_categories(api, database)
product.get_products(database, api)
# category.retrieve_category_data(database)
