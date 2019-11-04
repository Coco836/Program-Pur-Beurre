# Program-Pur-Beurre

## Documentation
The intention behind Pur Beurre request is to create a program that interacts with Open Food Facts data base. The program itself will manage to recover Open Food Facts data via its API (application programming interface). Then it will compare the product chosen by the user with another one and offers him a healthier substitute.

### Approach
- Installation of MySQL version 8.0 via the command prompt.
- Configuration of the software under Windows 10 and connexion to MySQL (host, username and password).
- Installing Python Modules:
    - pip install mysql-connector
    - pip install requests
- Creation of the data base named "__pur_beurre__".
- Create a class named "__Category__" in data base. This class has two attributes:
    - __id_category__, which corresponds to the index of each category of products. This attribute allows an exclusive number to be generated automatically everytime a new record is inserted into the table.
    - __name__, which simply corresponds to the name of each category of products.
