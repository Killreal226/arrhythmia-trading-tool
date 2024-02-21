import datetime

from tinkoff.invest import AsyncClient
from tinkoff.invest.schemas import OrderDirection, OrderType, PostOrderResponse

from app.service.arrhytmia_tools.dataclasses import StateInstrument
from app.config import config
from app.service.utils import float_to_quotation, get_id_from_time

class Conditions:
    def __init__(self) -> None:
        self.data_order_book = []
        self.state_instrument : StateInstrument = None
        self.max_allowed_time_in_minuts = datetime.timedelta(minutes=config.MAX_ALLOWED_TIME_IN_MINUTS)
        self.price_limit_order_buy = None
        self.volume_limit_order_buy = None

    def empty_state_instrument(self) -> bool:
        if (
            self.state_instrument.volume_in_portfolio == 0 and
            self.state_instrument.volume_limit_order_buy is None and
            self.state_instrument.volume_limit_order_sell is None
        ):
            return True
        else:
            return False
        
    def all_limit_orders_buy_executed(self) -> bool:
        if (
            self.state_instrument.volume_limit_order_buy is None and
            self.state_instrument.volume_in_portfolio != 0 and
            self.state_instrument.volume_limit_order_buy == self.state_instrument.volume_in_portfolio
        ):
            return True
        else:
            return False

    def time_for_limit_orders_sell_passed(self) -> bool:
        current_time = datetime.datetime.now()
        time_difference = current_time - self.state_instrument.time_create_limit_order_sell
        if time_difference > self.max_allowed_time_in_minuts:
            return True
        else:
            return False
        
    def favorable_market_situation_for_buy(self) -> bool:
        pass


class Events:
    def __init__(self) -> None:
        self._conditions = Conditions()
        self._api_token = config.API_TOKEN
        self._account_id = config.ID_ACCOUNT
        self.state_instruments: dict[str, StateInstrument] = {}

    def get_task_by_event(self, data_order_book: list, state_instrument: StateInstrument):
        self._conditions.data_order_book = data_order_book
        self._conditions.state_instrument = state_instrument
        self._conditions.price_limit_order_buy = None
        self._conditions.volume_limit_order_buy = None

        if state_instrument.volume_limit_order_buy is None and state_instrument.volume_in_portfolio == 0:
            state_instrument.volume_limit_order_sell = None

        if self._conditions.empty_state_instrument() and not self._conditions.favorable_market_situation_for_buy:
            self.state_instruments[state_instrument.figi] = state_instrument
            return None
        
        if self._conditions.empty_state_instrument() and self._conditions.favorable_market_situation_for_buy:
            return self._task_limit_order_buy(state_instrument)
        
        if (state_instrument.volume_limit_order_buy is None 
            and state_instrument.volume_in_portfolio != 0 and not self._conditions.time_for_limit_orders_sell_passed()
        ):
            self.state_instruments[state_instrument.figi] = state_instrument
            return None
        
        if (state_instrument.volume_limit_order_buy is None 
            and state_instrument.volume_in_portfolio != 0 
            and self._conditions.time_for_limit_orders_sell_passed()
            and state_instrument.volume_limit_order_sell is None
        ):
            return self._task_market_order_sell(state_instrument)

        if (state_instrument.volume_limit_order_buy is None 
            and state_instrument.volume_in_portfolio != 0 
            and self._conditions.time_for_limit_orders_sell_passed()
            and state_instrument.volume_limit_order_sell is not None
        ):
            return self._task_cancel_limit_order_sell(state_instrument)

    async def _task_limit_order_buy(self, state_instrument: StateInstrument) -> PostOrderResponse:
        async with AsyncClient(self._api_token) as client:
            response = await client.orders.post_order(               
                figi= state_instrument.figi,
                quantity=self._conditions.volume_limit_order_buy,
                price=float_to_quotation(self._conditions.price_limit_order_buy),
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                account_id=self._account_id,
                order_type=OrderType.ORDER_TYPE_LIMIT,
                order_id = get_id_from_time()
            )
            ## проверка результата
            self.state_instruments[state_instrument.figi] = state_instrument
            return response
        
    async def _task_market_order_sell(self, state_instrument: StateInstrument) -> PostOrderResponse:
        async with AsyncClient(self._api_token) as client:
            response = await client.orders.post_order(               
                figi= state_instrument.figi,
                quantity=self._conditions.volume_in_portfolio,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                account_id=self._account_id,
                order_type=OrderType.ORDER_TYPE_MARKET,
                order_id = get_id_from_time()
            )
            ## проверка результата
            self.state_instruments[state_instrument.figi] = state_instrument
            return response
        
    async def _task_cancel_limit_order_sell(self, state_instrument: StateInstrument) -> PostOrderResponse:
        pass
    