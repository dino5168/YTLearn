from lib_db.db.database import get_db


class DbUtils:
    def __init__(self):
        self.db = get_db()
        pass

    def hello(self):
        self.db

        print("hello")
