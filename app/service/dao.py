from app.base_dao import BaseDAO
from app.service.model import Transactions


class TransactionsDAO(BaseDAO):
    model = Transactions
