import csv
import datetime

from peewee import *

CSV_FILE_NAME = 'inventory.csv'

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=255, unique=True, null=False)
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


if __name__ == "__main__":
    #Setup conections, create table and load data from CSV
    db.connect()
    db.create_tables([Product], safe=True)
    write_db(read_csv(CSV_FILE_NAME))