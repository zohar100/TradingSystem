from datetime import datetime
from polygon_api.entities.bar_type_entity import BarType

class get_bars_dto:
    def __init__(self, type: BarType, symbol: str, start_date: datetime, end_date: datetime):
        self.type = type
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def __dict__(self):
        return {
            "type": self.type,
            "symbols": self.symbol,
            "startDate": self.start_date,
            "endDate": self.end_date
        }

