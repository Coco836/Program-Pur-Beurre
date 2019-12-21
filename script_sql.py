# -*- coding : utf8 -*-

create_db =	"""CREATE DATABASE pur_beurre_1 CHARACTER SET 'utf8';"""

create_category	= (
                   """CREATE TABLE Category (
                   id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
                   name VARCHAR (200) NOT NULL,
                   PRIMARY KEY (id))
                   ENGINE=INNODB;"""
)

create_product = (
                  """CREATE TABLE Product (
                  id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
                  name VARCHAR (200) NOT NULL UNIQUE,
                  description TEXT,
                  url VARCHAR (900) NOT NULL,
                  nutrition_grade VARCHAR (5),
                  PRIMARY KEY (id))
                  ENGINE=INNODB;"""
)

create_shop = (
               """CREATE TABLE Shop (
	           id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
               name VARCHAR (200) NOT NULL,
               PRIMARY KEY (id))
               ENGINE=INNODB;"""
)

create_link_prod_cat =	(
                         """CREATE TABLE Link_prod_cat (
                         id_category SMALLINT UNSIGNED NOT NULL,
                         id_product SMALLINT UNSIGNED NOT NULL,
                         PRIMARY KEY (id_category, id_product),
                         CONSTRAINT fk_category_id FOREIGN KEY (id_category)
                         REFERENCES Category(id) ON DELETE CASCADE,
                         CONSTRAINT fk_product_id FOREIGN KEY (id_product)
                         REFERENCES Product(id) ON DELETE CASCADE)
                         ENGINE=INNODB;"""
)


create_link_prod_shop =	(
                         """CREATE TABLE Link_prod_shop (
                         id_product SMALLINT UNSIGNED NOT NULL,
                         id_shop SMALLINT UNSIGNED NOT NULL,
                         PRIMARY KEY (id_product, id_shop),
                         CONSTRAINT fk_prod_id FOREIGN KEY (id_product)
                         REFERENCES Product(id) ON DELETE CASCADE,
                         CONSTRAINT fk_shop_id FOREIGN KEY (id_shop)
                         REFERENCES Shop(id) ON DELETE CASCADE)
                         ENGINE=INNODB;"""
)
