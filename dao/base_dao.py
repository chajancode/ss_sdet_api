from database import db
from database import Database


class BaseDao:
    def __init__(self, database: Database = db) -> None:
        self.db = database
