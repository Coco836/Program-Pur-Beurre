# Program-Pur-Beurre

## Documentation
The intention behind Pur Beurre request is to create a program that interacts with Open Food Facts data base. The program itself will manage to recover Open Food Facts data via its API (application programming interface). Then it will compare the product chosen by the user with another one and offers him a healthier substitute.

### Approach
- Installation of MySQL version 8.0 via the command prompt.
- Configuration of the software under Windows 10 and connexion to MySQL (host, username and password).
- Installing Python Modules:
    - pip install mysql-connector
    - pip install requests

#### Data Base
- Creation of the data base named "__pur_beurre__".
- Create a table named "__Category__" in data base. This table has two attributes:
    - __id__, which corresponds to the index of each category of products. This attribute allows an exclusive number to be generated automatically everytime a new record is inserted into the table.
    - __name__, which simply corresponds to the name of each category of products.
- Create a table named "__Product__" in data base. This table has several attributes:
    - __id__, which corresponds to the the index of each product. The index is generated automatically.
    - __name__, which corresponds to the name of the products.
    - __description__, which corresponds to the products' ingredients.
    - __nutrition_grade__, which corresponds to the nutriscore of a product.
    - __id_category__, which refers to the id of the category a product is in.
    - __id_substitute__, ???

#### Python program
- Creation of a class named "__OpenFoodFactsApi__", which retrieves API data via a "json" address.
    - Method "__fetch_categories_data_api__" allows the program to retrieves the different informations of the categories. This method filter the informations needed for the program and take out only the name of the categories and save them in a variable.
    - Method "__fetch_products_data_api__" allows the program to retrieves the different informations of the products in categories that were previously chosen. This method start by using the result of the previous method, then with some concatenation one is able to retrieves the json data of each categories. It returns a list of dictionnaries and each of them represent the data of one category. Each keys of the different dictionnaries have a list for value.
- Creation of a class named "__Category__", ...
