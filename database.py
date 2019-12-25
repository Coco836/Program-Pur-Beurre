# -*- coding : utf8 -*-

import mysql.connector
import script_sql as script


class DataBase:
    """ Connection to database 'pur_beurre' and execution of sql requests. """

    def __init__(self, user, passwd):
        # Connection to database pur_beurre with parameters
        self.create_database(user, passwd)
        self.my_data_base = mysql.connector.connect(
                                                    host="localhost",
                                                    user=user,
                                                    passwd=passwd,
                                                    database="pur_beurre",
                                                    buffered=True
        )
        #  Allows Python code to execute MySQL command in a database session.
        self.mycursor = self.my_data_base.cursor()
        self.create_tables()

    def execute(self, sql, values):
        """ Method allowing execution of sql request. """
        # Execute command sql in database.
        self.mycursor.execute(sql, values)
        # Commit: save data in data base table before closing connection.
        self.my_data_base.commit()

    def create_database(self, user, passwd):
        """
            Method allowing the creation of the database from
            an import script.
        """
        data_base = mysql.connector.connect(host="localhost", user=user, passwd=passwd)
        cursor = data_base.cursor()
        cursor.execute(script.create_db)
        cursor.close()

    def create_tables(self):
        """
            Method allowing the creation of the tables in the database
            pur_beurre from an import script.
        """
        creation_tables = [
                           script.create_category, script.create_product,
                           script.create_shop, script.create_link_prod_cat,
                           script.create_link_prod_shop
        ]
        for table in creation_tables:
            self.mycursor.execute(table)

    def close_database(self):
        """ Method to close connection to the database. """
        # Closing the connection
        self.my_data_base.close()
