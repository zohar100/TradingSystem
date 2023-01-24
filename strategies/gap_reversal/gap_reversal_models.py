import os
from typing import Any

from dotenv import load_dotenv
from decouple import config
from peewee import *

load_dotenv('../.env')

db_name = config('DB_NAME', 'gap_reversal')
db_user = config('DB_USER', 'postgres')
db_password = config('DB_PASSWORD', 'password')
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
    support = DecimalField(decimal_places=2, default=0.00)
    resistance = DecimalField(decimal_places=2, default=0.00)
    date = DateField()
    patterns=TextField(null=True)
    spy_gap=DecimalField(null=True)