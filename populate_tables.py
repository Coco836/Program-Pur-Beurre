# -*- coding : utf8 -*-
import program

# program.database.create_database()
program.Shop.get_shops(program.api, program.database)
program.Category.get_categories(program.api, program.database)
program.Product.get_products(program.api, program.database)
program.database.close_database()
