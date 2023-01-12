from datetime import datetime
from ..entities.bar_type_entity import BarType

class get_bars_dto:
    def __init__(self, type: BarType, symbols: list[str], start_date: datetime, end_date: datetime):
        self.type = type
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date

    def __dict__(self):
        return {
            "type": self.type,
            "symbols": self.symbols,
            "startDate": self.start_date,
            "endDate": self.end_date
        }

