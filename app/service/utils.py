import datetime

from tinkoff.invest.schemas import Quotation


def quotation_to_float(quotation: Quotation) -> float:
    return quotation.units + quotation.nano / 10**9

def float_to_quotation(value: float) -> Quotation:
    units = int(value)
    nano = int((value - units) * 10**9)
    return Quotation(units=units, nano=nano)

def get_id_from_time() -> str:
    now = datetime.now()
    date_string = now.strftime('%Y%m%d%H%M%S')
    return date_string