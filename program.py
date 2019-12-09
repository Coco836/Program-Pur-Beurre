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
        # Get only the data needed: data besides the one in the "tags"
        # list are irrelevant here.
        data_tags = json_data_file.get('tags')
        # Select only the name of each category (no need for other data).
        category_data = [
                        element.get('name', 'None') for element in data_tags
                        if "🍩" not in element.get('name', 'None')
                        ]
        return category_data

    def fetch_products_data_api(self, category: "Category"):
        url_categories = (
                        f'''https://fr.openfoodfacts.org/categorie/
                        {category.name}.json'''
        )
        response = requests.get(url_categories)
        json_data_file = response.json()
        data_products = json_data_file.get('products')
        return data_products

    def fetch_stores_data_api(self):
        response = requests.get('''https://fr.openfoodfacts.org/categorie/
                                stores.json'''
        )
        json_data_file = response.json()
        data_tags = json_data_file.get('tags')
        store_data = [element.get('name', 'None') for element in data_tags]
        return store_data


class Category:
    """docstring for Category."""

    def __init__(self, id = None, name = ''):
        self.id = id
        self.name = name


    @classmethod
    def get_categories(cls, api, database):
        category_data = api.fetch_categories_data_api()

        for name in category_data[:20]:
            values = [name]
            category = cls(name=name)
            category.save(database)

    def save(self, database):
        sql = "INSERT INTO category (name) VALUES (%s)"
        values = [self.name]
        database.execute(sql, values)

class Product:
    """docstring for Product."""

    def __init__(self, id = None, name = '', description = '',
                     url = '', nutrition_grade = ''):
        self.id = id
        self.name = name
        self.description = description
        self.url = url
        self.nutrition_grade = nutrition_grade

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
                prod_stores = data_product.get('stores')

                values = [
                    prod_name, prod_ingredients, prod_url, prod_nutriscore,
                ]
                product = cls(
                                name=prod_name, description=prod_ingredients,
                                url=prod_url, nutrition_grade=prod_nutriscore
                )
                product.save(database)

                last_id_product = database.mycursor.lastrowid
                last_id_cat = category.id

                product.link_prod_cat(database, prod_categories,
                                    last_id_product, last_id_cat)
                product.link_prod_shop(database, prod_stores, last_id_product)

    def save(self, database):
        sql = (
            '''INSERT INTO product (name, description, url,
            nutrition_grade) VALUES (%s, %s, %s, %s)'''
        )
        values = [self.name, self.description, self.url, self.nutrition_grade]
        database.execute(sql, values)

    def link_prod_cat(self, database, prod_categories, last_id_product,
                        last_id_cat):
        list_of_product_categories = prod_categories.split(',')

        for item in list_of_product_categories:
            list_of_product_categories = [
                                        item.strip() for item
                                        in list_of_product_categories
            ]

        for prod_category in list_of_product_categories:
            database.mycursor.execute("SELECT id FROM Category WHERE name = %s",
                                        (prod_category,)
            )
            myresult = database.mycursor.fetchone()
            sql = '''INSERT IGNORE INTO link_prod_cat
                (id_category, id_product) VALUES (%s, %s)'''

            if myresult != None:
                values = [myresult[0], last_id_product]
                database.execute(sql, values)
                # print("link_cat:", values)
            else:
                values = [last_id_cat, last_id_product]
                database.execute(sql, values)

    def link_prod_shop(self, database, prod_stores, last_id_product):
        if prod_stores != None:
            list_of_product_stores = prod_stores.split(',')
            for item in list_of_product_stores:
                list_of_product_stores = [
                                        item.strip() for item
                                        in list_of_product_stores
                ]

            for prod_store in list_of_product_stores:
                database.mycursor.execute("SELECT id FROM Shop WHERE name =%s",
                                            (prod_store,)
                )
                myresult = database.mycursor.fetchone()
                sql = '''INSERT IGNORE INTO link_prod_shop
                    (id_product, id_shop) VALUES (%s, %s)'''
                if myresult != None:
                    values = [last_id_product, myresult[0]]
                    database.execute(sql, values)


class Shop:
    """docstring for Shop."""

    def __init__(self, id = None, name = ''):
        self.id = id
        self.name = name

    @classmethod
    def get_shops(cls, api, database):
        store_data = api.fetch_stores_data_api()

        for name in store_data[:20]:
            values = [name]
            shop = cls(name=name)
            shop.save(database)

    def save(self, database):
        sql = "INSERT INTO Shop (name) VALUES (%s)"
        values = [self.name]
        database.execute(sql, values)


class DataBase:
    """docstring for DataBase."""

    def __init__(self):
        # Connection to database pur_beurre with parameters
        self.my_data_base = mysql.connector.connect(host="localhost",
                            user="colette", passwd="", database="pur_beurre",
                            buffered = True)
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

    def select_categories(self, limit = 20)-> list:
        self.mycursor.execute(f"SELECT id, name FROM Category limit {limit}")
        return [Category(id, name) for id, name in self.mycursor.fetchall()]

    def close_database(self):
        # Closing the connection
        self.my_data_base.close()



api = OpenFoodFactsApi()
database = DataBase()
# Shop.get_shops(api, database)
# Category.get_categories(api, database)
# Product.get_products(api, database)

while True:

    print("\nVoici les différentes catégories de produits disponibles !\n")
    database.mycursor.execute("SELECT * FROM Category")
    show_categories = database.mycursor.fetchall()
    for cat in show_categories:
        print(cat[0], "-", cat[1])

    message = (
    "\nEntrez l'id de la catégorie dont vous souhaitez"
    " voir les produits (doit être un nombre entier): "
    )
    choice_cat = int(input(message))

    while choice_cat > 20:
        message = (
        "\nCette id n'existe pas dans la base de données."
        " Veuillez choisir une id valide (qui ne dépasse pas 20): "
        )
        choice_cat = int(input(message))

    database.mycursor.execute(
    f'''SELECT product.id, product.name FROM Product
    INNER JOIN Link_prod_cat ON Product.id = Link_prod_cat.id_product
    INNER JOIN Category ON Link_prod_cat.id_category = Category.id
    WHERE Category.id = {choice_cat}'''
    )
    show_products = database.mycursor.fetchall()
    print("\n    Voici les produits de la catégorie n°", choice_cat, ":\n")
    for prod in show_products:
        print(prod[0], "-", prod[1])

    message = (
            "\nEntrez l'id du produit dont vous souhaitez"
            " voir les différents substituts possibles: "
    )
    choice_prod = input(message)

    database.mycursor.execute(
    f'''SELECT product.name, product.description, product.nutrition_grade,
    shop.name, product.url FROM Product
    INNER JOIN Link_prod_cat ON Product.id = Link_prod_cat.id_product
    INNER JOIN Link_prod_shop ON Link_prod_shop.id_product = Product.id
    INNER JOIN Shop ON Link_prod_shop.id_shop = Shop.id
    WHERE Link_prod_cat.id_category = {choice_cat}
    AND nutrition_grade IS NOT NULL ORDER BY nutrition_grade LIMIT 3'''
    )
    show_substitutes = database.mycursor.fetchall()
    print("\n    Voici le(s) substitut(s) du produit n°", choice_prod, ":\n")
    for subs in show_substitutes:
        print("Nom : ", subs[0], "\nDescription : ", subs[1],
                "\nNutriscore : ", subs[2], "\nMagasin où l'acheter : ",
                subs[3], "\nUrl produit : ", subs[4], "\n")

    message = (
            "\nVoulez vous choisir une nouvelle catégorie ?"
            " Entrez N pour quitter le programme. "
    )
    choice = input(message)
    if choice == "N":
        break

# INSERT INTO User_products (name, description, nutrition_grade, shop, url)
