from tinkoff.invest.schemas import Quotation


def quotation_to_float(quotation: Quotation) -> float:
    return quotation.units + quotation.nano / 10**9
