import queue
import time

from loguru import logger
from tinkoff.invest import (
    Client,
    MarketDataRequest,
    MarketDataResponse,
    OrderBookInstrument,
    SubscribeOrderBookRequest,
    SubscriptionAction,
    TradesStreamResponse,
)

from app.config import config
from app.service.events import TradeEvent
from app.service.utils import quotation_to_float


class BasicConnector:
    def __init__(self, queue: queue.Queue, stop_event) -> None:
        self._config = config
        self._api_token: str = config.API_TOKEN
        self._queue = queue
        self._stop_event = stop_event


class ConnectorOrderBook(BasicConnector):
    _data_order_book = {}

    def run(self) -> None:
        self._listen_order_book()

    def _listen_order_book(self) -> None:
        instruments_to_subscribe = self._get_instruments_to_subscribe()
        with Client(self._api_token) as client:
            for marketdata in client.market_data_stream.market_data_stream(
                self._request_iterator(instruments_to_subscribe)
            ):
                try:
                    self._update_queue(marketdata)
                except Exception as ex:
                    logger.info(f"Error in stream orderbook {ex}")

    def _get_instruments_to_subscribe(self) -> list[OrderBookInstrument]:
        result = []
        for ticker in self._config.DATA_TICKERS:
            result.append(
                OrderBookInstrument(figi=self._config.DATA_TICKERS[ticker]["figi"], depth=self._config.DEPTH_ORDER_BOOK)
            )
        return result

    def _request_iterator(self, instruments_to_subscribe: list[OrderBookInstrument]):
        yield MarketDataRequest(
            subscribe_order_book_request=SubscribeOrderBookRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=instruments_to_subscribe,
            )
        )
        while not self._stop_event.is_set():
            time.sleep(1)

    def _update_queue(self, marketdata: MarketDataResponse) -> None:
        self._update_data_order_book(marketdata)

        try:
            current_data_in_queue = self._queue.get_nowait()
        except queue.Empty:
            current_data_in_queue = None

        if current_data_in_queue is not None:
            current_data_in_queue.update(self._data_order_book)
            self._queue.put(current_data_in_queue)
        else:
            self._queue.put(self._data_order_book)

    def _update_data_order_book(self, marketdata: MarketDataResponse) -> None:
        figi = marketdata.orderbook.figi
        bids = marketdata.orderbook.bids
        for i, bid in enumerate(bids):
            price = quotation_to_float(bid.price)
            volume = bid.quantity
            bids[i] = {"price": price, "volume": volume}
        self._data_order_book[figi] = bids


class ConnectorTrades(BasicConnector):
    def run(self) -> None:
        self._listen_trades()

    def _listen_trades(self) -> None:
        with Client(self._api_token) as client:
            for marketdata in client.orders_stream.trades_stream(accounts=[self._config.ID_ACCOUNT]):
                if self._stop_event.is_set():
                    break
                try:
                    self._update_queue(marketdata)
                except Exception as ex:
                    logger.info(f"Error in stream portfolio {ex}")

    def _update_queue(self, marketdata: TradesStreamResponse) -> None:
        figi = marketdata.order_trades.figi
        direction = marketdata.order_trades.direction
        for trade in marketdata.order_trades.trades:
            time = trade.date_time
            price = trade.price
            volume = trade.quantity
            self._queue.put(TradeEvent(figi, time, direction, price, volume))
