import os
from typing import Any

from dotenv import load_dotenv
from decouple import config
from peewee import *

load_dotenv('../.env')

db_name = config('DB_NAME')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST', 'localhost')
db_port = config('DB_PORT', 5432)

db = PostgresqlDatabase(
    db_name, user=db_user, password=db_password, host=db_host, port=db_port)

class BaseModel(Model):
    class Meta():
        database = db


class ChosenStock(BaseModel):
    id = PrimaryKeyField()
    symbol = CharField(max_length=10)
    action = TextField()
    yesterday_close = DecimalField(decimal_places=2)
    today_open = DecimalField(decimal_places=2, default=0)
    gap = DecimalField(decimal_places=2)
    pre_market_volume = IntegerField()
    closest_support = DecimalField(decimal_places=2, default=0.00)
    next_closest_support = DecimalField(decimal_places=2, default=0.00)
    date = DateField()