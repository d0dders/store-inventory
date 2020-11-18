from collections import OrderedDict
import csv
import datetime
import os
from peewee import *
from models.product import Product, db


CSV_FILE_NAME = 'inventory.csv'


def read_csv(file):
    """Accepts a CSV file name, reads the contents of the file, and cleans it
    Returns the cleaned list
    """
    with open(file) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        product_list = list(csv_reader)
        #clean data
        for product in product_list:
            product['product_quantity'] = int(product['product_quantity'])
            product['product_price'] = int(float(product['product_price'][1:])*100)
            product['date_updated'] = datetime.datetime.strptime(product['date_updated'], "%m/%d/%Y")
        return product_list


def write_db(product_list):
    """Takes list of products and passes them to fucntion that will write or update to the db
    """
    for product in product_list:
        write_product_to_db(product)
        


def write_product_to_db(product):
    """Takes a dictionary of product details and writes it to the db
    Returns a string indicating whether the item was a new addition, or an update
    """
    write_type = None
    try:
        Product.create(
            product_name=product['product_name'],
            product_quantity=product['product_quantity'],
            product_price=product['product_price'],
            date_updated=product['date_updated']
        )
        write_type = 'CREATED'
    except IntegrityError:
        current_record = Product.get(product_name=product['product_name'])
        if current_record.date_updated < product['date_updated']:
            current_record.product_quantity=product['product_quantity']
            current_record.product_price=product['product_price']
            current_record.date_updated=product['date_updated']
            current_record.save()
            write_type = 'UPDATED'
    return write_type


def menu_loop():
    """Show the menu"""
    choice = None

    while choice != 'q':
        clear()
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()

        if choice in menu:
            clear()
            menu[choice]()
        elif choice == 'q':
            pass
        else:
            input("\nYou chose an invalid option. Hit ENTER to try again...")


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def add_product_screen():
    """Add a new product to the database"""
    while True:
        try:
            new_name = input("Enter product name:  ")
            if(len(new_name) <= 0):
                raise ValueError("Product name cannot be blank")
            new_quantity = int(input("Enter quantity:  "))
            new_price = int(input("Enter product price (cents):  "))
            new_date = datetime.datetime.now()
        except ValueError:
            print("You made an invalid entry") 
        else:
            new_product = {
                'product_name': new_name,
                'product_quantity': new_quantity,
                'product_price': new_price,
                'date_updated': new_date}  

            write_type = write_product_to_db(new_product)
            input(f"\nProduct {write_type} succesfully. Press ENTER to return to main menu...")
            break
        


def view_product_screen():
    """View a single product's inventory"""
    try:
        product_id = int(input("Enter a Product ID:  "))
        product = Product.get(product_id=product_id)
        print("\nProduct Name:", product.product_name)
        print("Quantity:", product.product_quantity)
        print("Price:", f'${product.product_price/100:.2f}')
        print("Last updated:", product.date_updated.strftime("%m/%d/%Y"))
        input("\nPress ENTER to return to main menu...")
    except ValueError:
        input("\nThe product ID must be a number. Press ENTER to continue...")
    except DoesNotExist:
        input("\nThat product doesn't exist. Press ENTER to continue...")


def backup_products():
    """Make a backup of the entire inventory"""
    #The following line is a convoluted method to programatically get column names
    fieldnames = (Product.get().__dict__)['__data__'].keys()
    products = Product.select().dicts()
    try:
        with open('backup.csv', 'w', newline="") as csv_file:
            productwriter = csv.DictWriter(csv_file, fieldnames=fieldnames)
            productwriter.writeheader()

            for product in products:
                productwriter.writerow(product)

        input("Backup saved as 'backup.csv'. Press ENTER to continue...")
    except Exception:
        input("WARNING: Something went wrong. Press ENTER to continue...")


menu = OrderedDict([
    ('a', add_product_screen),
    ('v', view_product_screen),
    ('b', backup_products)
])


if __name__ == "__main__":
    db.connect()
    db.create_tables([Product], safe=True)
    write_db(read_csv(CSV_FILE_NAME))

    menu_loop()