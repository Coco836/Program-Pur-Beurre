# Program-Pur-Beurre

## Documentation
The intention behind Pur Beurre request is to create a program that interacts with Open Food Facts database. The program itself will manage to recover Open Food Facts data via its API (application programming interface). Then it will compare the product chosen by the user with another one and offers him a healthier substitute.

### Approach
- Installation of MySQL version 8.0 via the command prompt.
- Configuration of the software under Windows 10 and connection to MySQL (host, username and password).
- Installing Python Modules:
    - __pip install -r requirements.txt__
- How to run the program:
    1. Run file __'populate_tables.py <user> [passwd]__'
    2. Run file __'interface.py <user> [passwd]'__

#### Database
- Creation of the database named "__pur_beurre__".
- Create a table named "__Category__" in database. This table has two attributes:
    - __id__, which corresponds to the index of each category of products. This attribute allows an exclusive number to be generated automatically every time a new record is inserted into the table.
    - __name__, which simply corresponds to the name of each category of products.
- Create a table named "__Product__" in database. This table has several attributes:
    - __id__, which corresponds to the the index of each product. The index is generated automatically.
    - __name__, which corresponds to the name of the products.
    - __description__, which corresponds to the products' ingredients.
    - __url__, which corresponds to the URL of a product.
    - __nutrition_grade__, which corresponds to the nutriscore of a product.
    - __favorites__, which can take only two values, false or true. The table is set as 'False (NULL)' but can change if the user choose to save a product as a substitute.
- Create a table named "__Shop__" in database. This table has two attributes:
    - __id__, which corresponds to the index of each store. The index is generated automatically.
    - __name__, which corresponds to the name of the stores.
- Create a table named "__Link_prod_cat__" in database. This table has two attributes:
    - __id_category__, which is a foreign key, referenced by 'id' from table 'Category'.
    - __id_product__, which is a foreign key, referenced by 'id' from table 'Product'.
- Create a table named "__Link_prod_shop__" in database. This table has two attributes:
    - __id_product__, which is a foreign key, referenced by 'id' from table 'Product'.
    - __id_shop__, which is a foreign key, referenced by 'id' from table 'Shop'.

#### Python program
- Creation of a class named "__OpenFoodFactsApi__", which retrieves API data via a "json" address.
    - Method "__fetch_stores_data_api__" allows the program to retrieve the information concerning the different stores existing in the API. The data needed are saved in a list.
    - Method "__fetch_categories_data_api__" allows the program to retrieve the different information concerning the categories of products. This method filter the information needed for the program and take out only the name of the categories and save them in a list.
    - Method "__fetch_products_data_api__" allows the program to retrieve the different information on the products in categories that were previously chosen. With the use of the class attribute 'name' from the object 'category', this method retrieves the name of categories one by one and concatenate it with the rest of the URL to take out the products' information of the categories.

- Creation of a class named "__Shop__", which inserts data concerning stores within the database.
    - Class method "__get_shops__" retrieves the list of stores' name, with a loop take out only 20 stores and call another method of the same class.
    - Method "__save__" is called by the previous method in order to save stores' information in the database.
    - Class method "__select_shop_names__" retrieves the values from table Shop according to the 'id' of a chosen substitute.

- Creation of a class named "__Category__", which inserts data concerning categories within the database.
    - Class method "__get_categories__" retrieves the list of categories' name, with a loop take out only 20 categories and call another method of the same class.
    - Method "__save__" is called by the previous method in order to save categories' information in the database.
    - Class method "__select_categories__" retrieves values from table Category.

- Creation of a class named "__Product__", which inserts data concerning product within the database.
    - Class method "__get_products__" retrieves products' information of every category, with a loop take out needed information of each product and call several other method of the same class.
    - Method "__save__" is called by the previous method in order to save products' information in the database.
    - Method "__link_prod_cat__" was created in order to link a product with the different categories it belongs to and insert into database the link using the 'id' of a product and the 'id' of a category.
    - Method "__link_prod_shop__" was created in order to link a product with the store it can be found in and insert into database the link using the 'id' of a product and the 'id' of a store.
    - Class method "__select_products__" retrieves products' values from a certain category chosen by the user of the program.
    - Static method "__select_nutriscore__" retrieves the nutriscore of a specific product chosen by the user.
    - Class method "__select_substitutes__" retrieves products' values of 3 different substitutes from a certain category chosen by the user and according to its nutriscore.
    - Static method "__update_favorites__" allows the value of the column favorites (table Product) to be changed to "true" when the user wants to save a substitute in the database.
    - Class method "__select_favorites__" retrieves information of saved products.

- Creation of a class named "__DataBase__", which allows the connection with the database.
    - Method "__execute__" allows the execution and the saving of the sql request made in other methods.
    - Method "__create_database__", which allows the creation of the database from another file.
    - Method "__close_database__" close the database after using it.

- Creation of a class named "__HumanComputerInteraction__" that takes care of everything related to the interactions between the user and the machine.
    - Method "__main_loop__", allows the program to run, calling different methods.
    - Method "__display_categories__" display the 20 categories in the program interface.
    - Method "__display_products__" display all the products from the chosen categories. Different other methods are called in order to prevent from an error within the program or to select the different products from a category in the database.
    - Method "__display_substitutes__" display the different substitutes of a product according to its nutriscore. Different other methods are called in order to prevent from an error, to select substitutes and also a method that give the possibility to save a substitute in the database as 'favorites'.
    - Method "__save_as_favorites__" give the possibility for the user to save or not a substitute as his favorites. If the user chose to save the product, another method will be called in order to change the value in the favorites' column.
    - Method "__display_favorites__" display the substitutes saved as favorites in database. The method that select favorites in database is called.
    - Private method "__try_block__" is used to prevent the program to stop in the command prompt when the program is running.
