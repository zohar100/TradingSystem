
from ..entities.bar_type_entity import BarType
from datetime import datetime

class get_bars_dto:
    def __init__(self, type: BarType, symbol: str, start_datetime: datetime, end_datetime: datetime):
        self.type =  type
        self.symbol = symbol
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def __dict__(self):
        return {
            "type": self.type,
            "symbol": self.symbol,
            "startDate": self.start_date,
            "endDate": self.end_date
        }