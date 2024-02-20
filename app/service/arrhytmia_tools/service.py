import asyncio
import queue

from tinkoff.invest.schemas import TradeDirection as TinkoffTradeDirection

from app.config import config
from app.service.arrhytmia_tools.dataclasses import StateInstrument
from app.service.arrhytmia_tools.events import Events
from app.service.arrhytmia_tools.utils import PreparingInstruments
from app.service.dao import TransactionsDAO
from app.service.events import TradeEvent


class ArrhytmiaService:
    def __init__(self, queue_order_book: queue.Queue, queue_trades: queue.Queue, stop_event) -> None:
        self._preparing_instrumets = PreparingInstruments()
        self._events = Events()
        self._state_instruments: dict[str, StateInstrument] = self._preparing_instrumets.create_dict_instruments()
        self._account_id = config.ID_ACCOUNT
        self._queue_order_book = queue_order_book
        self._queue_trades = queue_trades
        self._stop_event = stop_event
        self._async_tasks = []

    def run(self):
        while not self._stop_event.is_set():
            self._update_state_instruments_by_trades()
            self._get_tasks_by_data_order_book()
            results_async_tasks = asyncio.run(self._async_tasks)
            self._update_state_instruments_by_results(results_async_tasks)

    def _get_tasks_by_data_order_book(self) -> None:
        data_order_book = self._queue_order_book.get()
        for figi in data_order_book:
            async_task = self._events.get_task_by_event(data_order_book[figi], self._state_instruments[figi])
            if async_task:
                self._async_tasks.append(async_task)

    def _update_state_instruments_by_trades(self) -> None:
        while not self._queue_trades.empty():
            trade_event: TradeEvent = self._queue_trades.get()
            figi = trade_event.figi
            if trade_event.direction == TinkoffTradeDirection.TRADE_DIRECTION_BUY:
                self._state_instruments[figi].volume_in_portfolio += trade_event.volume
            else:
                self._state_instruments[figi].volume_in_portfolio -= trade_event.volume
            self._state_instruments[figi].time_create_limit_order_sell = trade_event.time

            ticker = self._state_instruments[figi].ticker
            self._add_trade_event_in_db(trade_event, ticker)

    def _add_trade_event_in_db(self, trade_event: TradeEvent, ticker: str) -> None:
        async_task = TransactionsDAO.add_one(
            figi=trade_event.figi,
            ticker=ticker,
            order_time=trade_event.time,
            price=trade_event.price,
            volume=trade_event.volume,
            direction=trade_event.direction,
            account_id=self._account_id,
        )
        self._async_tasks.append(async_task)

    def _update_state_instruments_by_results(self, results_async_tasks: list):
        pass
