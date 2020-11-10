from collections import OrderedDict
import csv
import datetime
import os

from peewee import *

CSV_FILE_NAME = 'inventory.csv'

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField()

    class Meta:
        database = db


def read_csv(file):
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
    for product in product_list:
        write_product_to_db(product)
        


def write_product_to_db(product):
    try:
        Product.create(
            product_name=product['product_name'],
            product_quantity=product['product_quantity'],
            product_price=product['product_price'],
            date_updated=product['date_updated']
        )
    except IntegrityError:
        current_record = Product.get(product_name=product['product_name'])
        if current_record.date_updated < product['date_updated']:
            current_record.product_quantity=product['product_quantity']
            current_record.product_price=product['product_price']
            current_record.date_updated=product['date_updated']
            current_record.save()


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
        else:
            input("\nYou chose an invalid option. Hit ENTER to try again...")


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def add_product_screen():
    """Add a new product"""
    while True:
        try:
            new_name = input("Enter product name:  ")
            if(len(new_name) <= 0):
                raise ValueError("Product name cannot be blank")
            new_quantity = int(input("Enter quantity:  "))
            new_price = int(input("Enter product price (cents):  "))
            new_date = datetime.datetime.now()
        except Exception:
            print("You made an invalid entry") 
        else:
            new_product = {
                'product_name': new_name,
                'product_quantity': new_quantity,
                'product_price': new_price,
                'date_updated': new_date}  

            write_product_to_db(new_product)
        


def view_product(product_id):
    """View a products details"""
    pass


def backup_products():
    """Backup products to CSV"""
    pass

menu = OrderedDict([
    ('a', add_product_screen),
    ('v', view_product),
    ('b', backup_products)
])


if __name__ == "__main__":
    #Setup conections, create table and load data from CSV
    db.connect()
    db.create_tables([Product], safe=True)
    write_db(read_csv(CSV_FILE_NAME))
    
    menu_loop()