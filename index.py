
from datetime import datetime
from bars_api.bars_api import bars_api
from bars_api.dto.get_bars_dto import get_bars_dto

start_date = datetime(2019, 8, 22, 10)
end_date = datetime(2019, 8, 22, 11)
params = get_bars_dto(1, ["AAPL"], start_date, end_date)
bars = bars_api.get_bars(params)

print(bars)