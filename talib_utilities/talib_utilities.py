

from .candlestick_pattern_label import candlestick_pattern_label


class talib_utilities:
    def get_candlestick_pattern_label(value: str):
        return candlestick_pattern_label[value]