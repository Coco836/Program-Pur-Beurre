# -*- coding : utf8 -*-


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
    def select_shop_names(cls, id_subs, database):
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
    def select_categories(cls, database, limit=20) -> list:
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
        categories = Category.select_categories(database)

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
    def select_products(cls, choice_cat, database):
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
    def select_nutriscore(choice_prod, database):
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
    def select_substitutes(cls, choice_cat, nutriscore, database):
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
    def update_favorites(choice_saving, id_subs, database):
        """
            Method allowing user to save the substitute(s) found by changing
            the boolean value of the column favorites from table Product.
        """
        sql = f"UPDATE product SET favorites = (%s) WHERE id = {id_subs}"
        values = [choice_saving]
        database.execute(sql, values)

    @classmethod
    def select_favorites(cls, database):
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
