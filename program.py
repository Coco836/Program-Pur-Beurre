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

    def fetch_products_data_api(self, category: "Category"):
        url_categories = (f'https://fr.openfoodfacts.org/categorie/{category.name}.json')
        response = requests.get(url_categories)
        json_data_file = response.json()
        data_products = json_data_file.get('products')
        return data_products


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

    def __init__(self, id = None, name = '', description = '',
                     url = '', nutrition_grade = '', substitute = ''):
        self.id = id
        self.name = name
        self.description = description
        self.url = url
        self.nutrition_grade = nutrition_grade
        self.substitute = substitute

    @classmethod
    def get_products(cls, api, database):
        categories = database.select_categories()

        for category in categories:
            data_products = api.fetch_products_data_api(category)
            for data_product in data_products:
                prod_name = data_product.get('product_name', 'None')
                prod_ingredients = data_product.get('ingredients_text_fr')
                prod_url = data_product.get('url')
                prod_nutriscore = data_product.get('nutrition_grade_fr')
                prod_categories = data_product.get('categories')

                values = [
                    prod_name, prod_ingredients, prod_url, prod_nutriscore,
                ]
                sql = (
                    "INSERT INTO product (name, description, url, "
                    "nutrition_grade) VALUES (%s, %s, %s, %s)"
                )
                database.execute(sql, values)

                last_id_product = database.mycursor.lastrowid
                last_id_cat = category.id

                product.link_prod_cat(database, prod_categories, last_id_product, last_id_cat)


    def link_prod_cat(self, database, prod_categories, last_id_product, last_id_cat):
        list_of_product_categories = prod_categories.split(',')

        for item in list_of_product_categories:
            list_of_product_categories = [item.strip() for item in list_of_product_categories]

        for prod_category in list_of_product_categories:
            database.mycursor.execute("SELECT id FROM Category WHERE name = %s", (prod_category,))
            myresult = database.mycursor.fetchone()
            sql = "INSERT IGNORE INTO link_prod_cat (id_category, id_product) VALUES (%s, %s)"

            if myresult != None:
                values = [myresult[0], last_id_product]
                database.execute(sql, values)
            else:
                values = [last_id_cat, last_id_product]
                database.execute(sql, values)


    def get_substitutes(self, database):
        database.alter_table_product()
        products = database.select_products()
        for product in products:
            # if product.nutrition_grade != "a":
            #     database.mycursor.execute(
            #                             "SELECT id_product FROM Link_prod_cat "
            #                             "INNER JOIN Product "
            #                             "ON Product.id = Link_prod_cat.id_product "
            #                             "WHERE Link_prod_cat.id_product = %s", (product.id,)
            #                             )
            #     myresult = database.mycursor.fetchone()
            #     print(product.name, myresult)

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

    def select_categories(self, limit = 20)-> list:
        self.mycursor.execute(f"SELECT id, name FROM Category limit {limit}")
        return [Category(id, name) for id, name in self.mycursor.fetchall()]

    def alter_table_product(self):
        self.mycursor.execute("ALTER TABLE Product ADD id_substitute SMALLINT UNSIGNED")

    def select_products(self):
        self.mycursor.execute(f"SELECT id, name, description, url, nutrition_grade FROM Product")
        return [
                Product(id, name, description, url, nutrition_grade)
                for id, name, description, url, nutrition_grade
                in self.mycursor.fetchall()
        ]


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
# category.get_categories(api, database)
# product.get_products(api, database)
# product.link_prod_cat()
product.get_substitutes(database)
# category.retrieve_category_data(database)
