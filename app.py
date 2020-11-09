import csv
import datetime

from peewee import *

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

if __name__ == "__main__":
    print(read_csv('inventory.csv'))
    db.connect()
    db.create_tables([Product], safe=True)