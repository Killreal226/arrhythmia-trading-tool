import asyncio

from tinkoff.invest import AsyncClient, InstrumentIdType

from app.config import config
from app.service.arrhytmia_tools.dataclasses import StateInstrument
from app.service.utils import quotation_to_float


class PreparingInstruments:
    def __init__(self) -> None:
        self._config = config
        self._api_token = config.API_TOKEN

    def create_dict_instruments(self) -> dict[str, StateInstrument]:
        instruments = {}
        min_steps_prices = asyncio.run(self._get_list_min_steps_prices())
        for ticker, min_step_price in zip(self._config.DATA_TICKERS, min_steps_prices):
            figi = self._config.DATA_TICKERS[ticker]["figi"]
            instrument = StateInstrument(ticker=ticker, figi=figi, min_step_price=min_step_price)
            instruments[figi] = instrument
        return instruments

    async def _get_list_min_steps_prices(self) -> list[float]:
        tasks = []
        for ticker in self._config.DATA_TICKERS:
            figi = self._config.DATA_TICKERS[ticker]["figi"]
            task = self._get_min_step_price(figi)
            tasks.append(task)
        min_steps_prices = await asyncio.gather(*tasks)
        return min_steps_prices
    
    async def _get_min_step_price(self, figi: str) -> float:
        async with AsyncClient(self._api_token) as client:
            response = await client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi)
            min_step_price = quotation_to_float(response.instrument.min_price_increment)
            return min_step_price
