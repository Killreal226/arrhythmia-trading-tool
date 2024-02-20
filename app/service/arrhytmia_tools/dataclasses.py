import datetime
from dataclasses import dataclass


@dataclass(init=False)
class StateInstrument:
    ticker: str
    figi: str
    min_step_price: float
    volume_in_portfolio: int
    volume_limit_order_buy: int
    price_limit_order_buy: float
    time_create_limit_order_sell: datetime.datetime
    volume_limit_order_sell: int
    price_limit_order_sell: float

    def __init__(self, ticker, figi, min_step_price) -> None:
        self.ticker = ticker
        self.figi = figi
        self.min_step_price = min_step_price
        self.volume_in_portfolio = 0
        self.volume_limit_order_buy = None
        self.price_limit_order_buy = None
        self.time_create_limit_order_sell = None
        self.volume_limit_order_sell = None
        self.price_limit_order_sell = None
