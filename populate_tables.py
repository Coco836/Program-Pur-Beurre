# -*- coding : utf8 -*-
import api
import database as db
from orm import Shop, Category, Product
import sys

# Insertion of user's host name and password when starting the program
user = sys.argv[1]
if len(sys.argv) > 2:
    passwd = sys.argv[2]
else:
    passwd = None

api = api.OpenFoodFactsApi()
database = db.DataBase(user, passwd)

Shop.get_shops(api, database)
Category.get_categories(api, database)
Product.get_products(api, database)
database.close_database()
