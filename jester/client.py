from functools import wraps
from socket import socket

from jester.common import SocketParser


_FETCH_MAP = {"fetch_one": 0, "fetch_all": 1, "fetch_many": 2}


def _auto_complete(func):
    @wraps(func)
    def wrapper(self, statement: str, *args):
        func(self, statement, *args)  # Confirm that valid arguments were used
        payload = {
                "id": 0,
                "statement": statement,
                "method": func.__name__
            }
        if args:
            payload['args'] = list(args)
        self.send(payload)
        return self
    return wrapper


def _auto_fetch(func):
    @wraps(func)
    def wrapper(self, size: int=None):
        if func.__name__ != 'fetch_many' and size:
            raise TypeError(func.__name__ + "() takes 1 positional argument but 2 were given")
        payload = {
            "id": 1,
            "return": _FETCH_MAP[func.__name__]
        }
        if size:
            payload['size'] = size
        self.send(payload)
        response = self.get_payload()
        self.check_error(response)
        return response['resp']
    return wrapper


class JesterError(Exception):
    pass


class JesterClient(SocketParser):
    
    def __init__(self, addr: tuple = ('localhost', 27345)):
        super().__init__(socket())
        self.addr = addr

    def connect(self):
        self.conn.connect(self.addr)

    def close(self):
        self.conn.close()

    @_auto_complete
    def execute(self, statement: str, *args):
        pass

    @_auto_complete
    def execute_many(self, statement: str, values: list):
        pass

    @_auto_complete
    def execute_script(self, script: str):
        pass

    @staticmethod
    def check_error(response):
        if response['id'] == -1:
            raise JesterError(response['msg'])

    @_auto_fetch
    def fetch_one(self):
        pass

    @_auto_fetch
    def fetch_all(self):
        pass

    @_auto_fetch
    def fetch_many(self, size: int):
        pass

    def __iter__(self):
        return iter(
            self.fetch_all()
        )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
