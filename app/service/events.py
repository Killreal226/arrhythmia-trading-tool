import datetime
from dataclasses import dataclass
from enum import Enum

from tinkoff.invest.schemas import Quotation
from tinkoff.invest.schemas import TradeDirection as TinkoffTradeDirection

from app.service.utils import quotation_to_float


class TradeDirection(Enum):
    SELL = 0
    BUY = 1


@dataclass(init=False)
class TradeEvent:
    figi: str
    time: datetime.datetime
    direction: TradeDirection
    price: float
    volume: float

    def __init__(self, figi, time, direction, price, volume) -> None:
        self.figi = figi
        self.time = time
        if direction == TinkoffTradeDirection.TRADE_DIRECTION_BUY:
            self.direction = TradeDirection.BUY
        else:
            self.direction = TradeDirection.SELL
        if isinstance(price, Quotation):
            self.price = quotation_to_float(price)
        else:
            self.price = price
        if isinstance(volume, Quotation):
            self.volume = quotation_to_float(volume)
        else:
            self.volume = volume
