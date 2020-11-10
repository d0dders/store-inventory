from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField()

    class Meta:
        database = db