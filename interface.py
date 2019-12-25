from orm import Shop, Category, Product
import database as db
import sys
from colorama import init
from colorama import Fore, Back, Style


class HumanComputerInteraction:
    """ Creation of an interface for the program in the terminal. """

    def __init__(self, database):
        self.database = database
        init()

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
        show_categories = Category.select_categories(self.database)
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
        show_products = Product.select_products(choice_cat, self.database)
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
        nutriscore = Product.select_nutriscore(choice_prod, self.database)
        # Retrieve variable with three substitutes for the chosen product
        show_substitutes = Product.select_substitutes(choice_cat, nutriscore, self.database)
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
                show_shops = Shop.select_shop_names(id_subs, self.database)
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
            Product.update_favorites(choice_saving, id_subs, self.database)

    def display_favorites(self):
        """ Method that will display the saved substitutes on the terminal. """
        # Retrieve variable containing saved substitutes
        show_favorites = Product.select_favorites(self.database)
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
            show_shops = Shop.select_shop_names(id_subs, self.database)
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
                # the valid list, then try another with another value
                else:
                    print(Fore.RED + error_message + Fore.WHITE)
        return choice

# Insertion of user's host name and password when starting the program
if __name__ == '__main__':
    user = sys.argv[1]
    if len(sys.argv) > 2:
        passwd = sys.argv[2]
    else:
        passwd = None
    database = db.DataBase(user, passwd)
    interface = HumanComputerInteraction(database)
    interface.main_loop()
database.close_database()
