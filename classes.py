# -*- coding : utf8 -*-

import mysql.connector
import script_sql as script
import requests
from colorama import init
from colorama import Fore, Back, Style
init()


class OpenFoodFactsApi:
    """ Retrieve different data from online API."""

    def fetch_stores_data_api(self):
        """
            Method allowing the program to search stores' data online
            with the Open Food Facts API.
        """
        # Recover data from Open Food Facts URL API with request get.
        response = requests.get(
                                "https://fr.openfoodfacts.org/categorie/"
                                "stores.json"
        )
        # Save the json data in a variable.
        json_data_file = response.json()
        # Get only the data needed: data besides the one in the "tags"
        # list are irrelevant here.
        data_tags = json_data_file.get('tags')
        # Select only the name of each store (no need for other data).
        store_data = [element.get('name', 'None') for element in data_tags]
        return store_data

    def fetch_categories_data_api(self):
        """
            Method allowing the program to search categories' data online
            with the Open Food Facts API.
        """
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
        """
            Method allowing the program to search products' data online
            with the Open Food Facts API.
        """
        # With the name of each category saved inside the database, do a
        # concatenation with the name of the category and the rest of the URL
        url_categories = (
                        f'''https://fr.openfoodfacts.org/categorie/
                        {category.name}.json'''
        )
        # Recover data from Open Food Facts URL API with request get.
        response = requests.get(url_categories)
        # Save the json data in a variable.
        json_data_file = response.json()
        # Get only the data needed: data besides the one in the "products"
        # list are irrelevant here.
        data_products = json_data_file.get('products')
        return data_products


class Shop:
    """ Insertion of stores' data inside database 'pur_beurre'. """

    def __init__(self, id=None, name=''):
        self.id = id
        self.name = name

    @classmethod
    def get_shops(cls, api, database):
        """ Method retrieving stores in order to save them into database. """
        # Retrieve list of stores' name
        store_data = api.fetch_stores_data_api()

        for name in store_data[:20]:
            shop = cls(name=name)
            shop.save(database)

    def save(self, database):
        """ Method allowing data to be saved in database."""
        sql = "INSERT INTO Shop (name) VALUES (%s)"
        values = [self.name]
        database.execute(sql, values)

    @classmethod
    def select_shop_names(cls, id_subs):
        """
            Method that retrieves the names of the different store where
            one can buy a substitute.
        """
        database.mycursor.execute(
                                  f'''SELECT id, name FROM Shop
                                  JOIN Link_prod_shop
                                  ON Link_prod_shop.id_shop = Shop.id
                                  WHERE Link_prod_shop.id_product =
                                  {id_subs}'''
        )
        return [cls(id, name) for id, name in database.mycursor.fetchall()]


class Category:
    """ Insertion of categories' data inside database 'pur_beurre'. """

    def __init__(self, id=None, name=''):
        self.id = id
        self.name = name

    @classmethod
    def get_categories(cls, api, database):
        """Method retrieving categories in order to save them into database."""
        # Retrieve list of categories' name
        category_data = api.fetch_categories_data_api()

        for name in category_data[:20]:
            category = cls(name=name)
            category.save(database)

    def save(self, database):
        """Method allowing data to be saved in database."""
        sql = "INSERT INTO category (name) VALUES (%s)"
        values = [self.name]
        database.execute(sql, values)

    @classmethod
    def select_categories(cls, limit=20) -> list:
        """ Method that retrieves categories from database. """
        # Retrieve all categories from database
        database.mycursor.execute(
                                f'''SELECT id, name FROM Category limit
                                {limit}'''
        )
        return [cls(id, name) for id, name in database.mycursor.fetchall()]


class Product:
    """ Insertion of products' data inside database 'pur_beurre'. """

    def __init__(self, id=None, name='', description='',
                 url='', nutrition_grade=''):
        self.id = id
        self.name = name
        self.description = description
        self.url = url
        self.nutrition_grade = nutrition_grade

    @classmethod
    def get_products(cls, api, database):
        """ Method retrieving products in order to save them into database."""
        # Retrieve categories' data from database
        categories = Category.select_categories()

        for category in categories:
            # Call method to search products in api and send category
            data_products = api.fetch_products_data_api(category)
            # For each products' data retrieve only needed ones per product
            for data_product in data_products:
                prod_name = data_product.get('product_name', 'None')
                prod_ingredients = data_product.get('ingredients_text_fr')
                prod_url = data_product.get('url')
                prod_nutriscore = data_product.get('nutrition_grade_fr')

                prod_categories = data_product.get('categories')
                prod_stores = data_product.get('stores')

                product = cls(
                                name=prod_name, description=prod_ingredients,
                                url=prod_url, nutrition_grade=prod_nutriscore
                )
                product.save(database)

                # Retrieve the last product inserted in database
                last_id_product = database.mycursor.lastrowid
                # Retrieve the last category inserted in database
                last_id_cat = category.id

                product.link_prod_cat(database, prod_categories,
                                      last_id_product, last_id_cat)
                product.link_prod_shop(database, prod_stores, last_id_product)
        # database.add_column_to_product()

    def save(self, database):
        """ Method allowing data to be saved in database."""
        sql = (
            '''INSERT IGNORE INTO product (name, description, url,
            nutrition_grade) VALUES (%s, %s, %s, %s)'''
        )
        values = [self.name, self.description, self.url, self.nutrition_grade]
        database.execute(sql, values)

    def link_prod_cat(self, database, prod_categories, last_id_product,
                      last_id_cat):
        ''' Method allowing a product to be linked with different categories'''
        # Retrieve a list of the different categories to which the current
        # inserted product belongs
        list_of_product_categories = prod_categories.split(',')

        # For each category's name inside the list if it exists in database,
        # and if it does, retrieve the id of the category in question
        for prod_category in list_of_product_categories:
            database.mycursor.execute(
                                      "SELECT id FROM Category WHERE "
                                      "name = %s", (prod_category.strip(),)
            )
            myresult = database.mycursor.fetchone()
            sql = '''INSERT IGNORE INTO link_prod_cat
                (id_category, id_product) VALUES (%s, %s)'''

            # If a category's name does exist in database, insert the link
            # between a product and its categories with their ids
            if myresult is not None:
                values = [myresult[0], last_id_product]
                database.execute(sql, values)
            # If none of the categories' name (to which product belongs) exist
            # in database, then the current inserted product will be linked
            # with the id of the category in which it was found in the API.
            else:
                values = [last_id_cat, last_id_product]
                database.execute(sql, values)

    def link_prod_shop(self, database, prod_stores, last_id_product):
        """ Method allowing a product to be linked with store(s)"""
        # If the product is present in a store, retrieve a list of the
        # different stores to which the current inserted product belongs
        if prod_stores is not None:
            list_of_product_stores = prod_stores.split(',')

            # For each store's name inside the list if it exists in database,
            # and if it does, retrieve the id of the store in question
            for prod_store in list_of_product_stores:
                database.mycursor.execute(
                                          "SELECT id FROM Shop WHERE name =%s",
                                          (prod_store.strip(),)
                )
                myresult = database.mycursor.fetchone()
                sql = '''INSERT IGNORE INTO link_prod_shop
                    (id_product, id_shop) VALUES (%s, %s)'''

                # If a store's name does exist in database, insert the link
                # between a product and its stores with their ids
                if myresult is not None:
                    values = [last_id_product, myresult[0]]
                    database.execute(sql, values)

    @classmethod
    def select_products(cls, choice_cat):
        """
            Method that retrieves products of the category chosen by the user,
            from database.
        """
        database.mycursor.execute(
                                  f'''SELECT product.id, product.name
                                  FROM Product INNER JOIN Link_prod_cat
                                  ON Product.id = Link_prod_cat.id_product
                                  INNER JOIN Category ON
                                  Link_prod_cat.id_category = Category.id
                                  WHERE Category.id = {choice_cat}'''
        )
        return [cls(id, name) for id, name in database.mycursor.fetchall()]

    @staticmethod
    def select_nutriscore(choice_prod):
        """
            Method that retrieves nutriscore of the product chosen by the user,
            from database.
        """
        database.mycursor.execute(
                                  f'''SELECT nutrition_grade FROM Product
                                  WHERE id = {choice_prod}'''
        )
        return database.mycursor.fetchone()[0]

    @classmethod
    def select_substitutes(cls, choice_cat, nutriscore):
        """
            Method that retrieves three substitutes for the product chosen by
            the user, inside the category initially chosen and take only
            other products with equal or greater nutriscore.
        """
        database.mycursor.execute(
                                  f'''SELECT id, name, description,
                                  url, nutrition_grade FROM Product
                                  INNER JOIN Link_prod_cat
                                  ON Product.id = Link_prod_cat.id_product
                                  WHERE Link_prod_cat.id_category =
                                  {choice_cat} AND nutrition_grade IS NOT NULL
                                  AND nutrition_grade <= "{nutriscore}"
                                  ORDER BY nutrition_grade LIMIT 3'''
        )
        return [
                cls(id, name, description, url, nutrition_grade)
                for id, name, description, url, nutrition_grade
                in database.mycursor.fetchall()
        ]

    @staticmethod
    def update_favorites(choice_saving, id_subs):
        """
            Method allowing user to save the substitute(s) found by changing
            the boolean value of the column favorites from table Product.
        """
        sql = f"UPDATE product SET favorites = (%s) WHERE id = '{id_subs}'"
        values = [choice_saving]
        database.execute(sql, values)

    @classmethod
    def select_favorites(cls):
        """ Method that retrieves all the substitutes that were saved in db."""
        database.mycursor.execute(
                                "SELECT id, name, description, "
                                "nutrition_grade, url "
                                "FROM Product "
                                "WHERE product.favorites = 1"
        )
        return [
                cls(id, name, description, url, nutrition_grade)
                for id, name, description, url, nutrition_grade
                in database.mycursor.fetchall()
        ]


class DataBase:
    """ Connection to database 'pur_beurre' and execution of sql requests. """

    def __init__(self):
        # Connection to database pur_beurre with parameters
        self.my_data_base = mysql.connector.connect(
                                                    host="localhost",
                                                    user="colette",
                                                    passwd="",
                                                    database="pur_beurre",
                                                    buffered=True
        )
        #  Allows Python code to execute MySQL command in a database session.
        self.mycursor = self.my_data_base.cursor()

    def execute(self, sql, values):
        """ Method allowing execution of sql request. """
        # Execute command sql in database.
        self.mycursor.execute(sql, values)
        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()

    # def create_database(self):
    #     """
    #         Method allowing the creation of the database from
    #         an import script
    #     """
    #     self.mycursor.execute(script.create_db)
    #     creation_tables = [
    #                        script.create_category, script.create_product,
    #                        script.create_shop, script.create_link_prod_cat,
    #                        script.create_link_prod_shop
    #     ]
    #     for table in creation_tables:
    #         self.mycursor.execute(table)

    def close_database(self):
        """ Method to close connection to the database. """
        # Closing the connection
        self.my_data_base.close()


class HumanComputerInteraction:
    """ Creation of an interface for the program in the terminal. """

    def main_loop(self):
        """ Method to enter the interface of the program. """
        # Enter program loop
        while True:
            print(
                  Fore.YELLOW + "\nBienvenue dans le programme de notre "
                  "startup PurBeurre !" + Fore.WHITE
            )
            # Create variables that will be sent to _try_block
            message = (
                        "\nChoisissez l'une des deux propositions"
                        " (tapez 1 ou 2)."
                        "\n  1 - Quel aliment souhaitez-vous remplacer ?\n"
                        "  2 - Retrouver mes aliments substitués.\nChoix : "
                        )
            # Create list of only valid propositions
            valid_ids = [1, 2]
            error_message = (
                            "\nCette proposition n'existe pas, "
                            "veuillez choisir entre 1 ou 2. "
            )
            # Return the proposition selected by the user while calling
            # method _try_block that prevent error to occurs.
            entry_choice = self._try_block(message, error_message, valid_ids)
            if entry_choice == 1:
                show_categories = self.display_categories()
                (show_products, choice_cat) = (
                                                self.display_products
                                                (show_categories)
                )
                (show_substitutes, name_subs) = (
                                                self.display_substitutes
                                                (show_products,
                                                 choice_cat)
                )
            if entry_choice == 2:
                self.display_favorites()

            final_message = (
                    "\nVoulez vous revenir au menu ?"
                    " Entrez N pour quitter le programme. "
            )
            final_choice = input(final_message)
            if final_choice == "N":
                break

    def display_categories(self):
        """ Method that will display the categories on the terminal. """
        print(
                Fore.GREEN + "\nVoici les différentes catégories de produits"
                "disponibles !\n" + Fore.WHITE
        )
        # Retrieve variable with all categories present in database
        show_categories = Category.select_categories()
        # Display all categories' id and name one by one
        for cat in show_categories:
            print(cat.id, Fore.CYAN + "-" + Fore.WHITE, cat.name)
        return show_categories

    def display_products(self, show_categories):
        """ Method that will display the products on the terminal. """
        # Create variables that will be sent to _try_block
        message = (
                   "\nEntrez l'id de la catégorie dont vous souhaitez"
                   " voir les produits (doit être un nombre entier): "
        )
        valid_ids = [cat.id for cat in show_categories]
        error_message = (
                         "\nCette id n'existe pas dans la base de données."
                         " Veuillez choisir une id valide."
        )
        # Return the proposition selected by the user while calling
        # method _try_block that prevent error to occurs.
        choice_cat = self._try_block(message, error_message, valid_ids)

        print(
                Fore.GREEN + "\n    Voici les produits de la catégorie n°",
                choice_cat, ":\n" + Fore.WHITE
        )
        # Retrieve variable with all product from the chosen category
        show_products = Product.select_products(choice_cat)
        # Display products' id and name one by one from the chosen category
        for prod in show_products:
            print(prod.id, Fore.CYAN + "-" + Fore.WHITE, prod.name)
        return show_products, choice_cat

    def display_substitutes(self, show_products, choice_cat):
        """ Method that will display the substitutes on the terminal. """
        # Create variables that will be sent to _try_block
        message = (
                "\nEntrez l'id du produit dont vous souhaitez"
                " voir les différents substituts possibles: "
        )
        valid_ids = [prod.id for prod in show_products]
        error_message = (
                         "\nCette id ne correspond pas à un produit de la "
                         "catégorie choisie. Veuillez choisir une id valide."
        )

        # Return the proposition selected by the user while calling
        # method _try_block that prevent error to occurs.
        choice_prod = self._try_block(message, error_message, valid_ids)
        # Return nutriscore of the chosen product from database
        nutriscore = Product.select_nutriscore(choice_prod)
        # Retrieve variable with three substitutes for the chosen product
        show_substitutes = Product.select_substitutes(choice_cat, nutriscore)
        # If a substitute (or max 3) exists display it (or them, one by one)
        if show_substitutes is not False:
            print(
                    Fore.GREEN + "\n   Voici le(s) substitut(s) du produit n°",
                    choice_prod, ":\n" + Fore.WHITE
            )
            for num_subs, subs in enumerate(show_substitutes, 1):
                # Create variable that will be sent as a parameter for method
                id_subs = subs.id
                print(
                        Fore.CYAN + "\nNom : " + Fore.WHITE, subs.name,
                        Fore.CYAN + "\nDescription : " + Fore.WHITE,
                        subs.description, Fore.CYAN + "\nNutriscore : " +
                        Fore.WHITE, subs.nutrition_grade, Fore.CYAN +
                        "\nUrl produit : " + Fore.WHITE, subs.url
                )
                show_shops = Shop.select_shop_names(id_subs)
                for shops in show_shops:
                    print(
                          Fore.CYAN + "Magasin où l'acheter : " + Fore.WHITE,
                          shops.name, "\n"
                    )
                # Call method that allows the user to save or not the result
                self.save_as_favorites(num_subs, id_subs)

        # If there is no substitute for a product just print a message
        else:
            print(
                  Fore.RED + "Il n'existe pas de substitut pour ce "
                  "produit" + Fore.WHITE
            )
        return show_substitutes, id_subs

    def save_as_favorites(self, num_subs, id_subs):
        """
            Method that will allows the user to choose whether he wants to
            save a substitutes or not.
        """
        # Create variables that will be sent to _try_block
        message = (
                    f"\nVoulez-vous enregistrer le substitut n°{num_subs} "
                    "en tant que favoris ? Tapez 1 pour OUI "
                    "ou 0 pour NON. "
        )
        valid_ids = [0, 1]
        error_message = ("\nVeuillez entrez 0 ou 1 !")
        # Return the proposition selected by the user while calling
        # method _try_block that prevent error to occurs.
        choice_saving = self._try_block(message, error_message, valid_ids)
        if choice_saving == 1:
            Product.update_favorites(choice_saving, id_subs)

    def display_favorites(self):
        """ Method that will display the saved substitutes on the terminal. """
        # Retrieve variable containing saved substitutes
        show_favorites = Product.select_favorites()
        # Display saved substituted one by one
        for fav in show_favorites:
            id_subs = fav.id
            print(
                  Fore.CYAN + "\nNom substitut: " + Fore.WHITE,
                  fav.name, Fore.CYAN + "\nDescription :" + Fore.WHITE,
                  fav.description, Fore.CYAN + "\nNutriscore :" + Fore.WHITE,
                  fav.nutrition_grade, Fore.CYAN + "\nURL : " + Fore.WHITE,
                  fav.url
            )
            show_shops = Shop.select_shop_names(id_subs)
            for shops in show_shops:
                print(
                      Fore.CYAN + "Magasin : " + Fore.WHITE,
                      shops.name, "\n"
                )

    def _try_block(self, message, error_message, valid_ids):
        """
            Private method that will prevent the program to stop
            (prevent error).
        """
        # Enter loop until a valid choice is made
        while True:
            # Try the choice made by the user
            try:
                choice = int(input(message))
            # If ValueError occurs, try again with another choice
            except ValueError:
                print(Fore.RED + error_message + Fore.WHITE)
            # If no ValueError and the choice is inside the valid_ids list,
            # the program continues
            else:
                if choice in valid_ids:
                    break
                # Despite the no ValueError, if the choice is not inside
                # the valid list, then try another choice
                else:
                    print(Fore.RED + error_message + Fore.WHITE)
        return choice


api = OpenFoodFactsApi()
database = DataBase()
