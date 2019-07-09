from gevent.monkey import patch_all; patch_all()

from functools import wraps
import logging
import sqlite3 as sql
from uuid import uuid4

from jester.common import invalid_body, invalid_method, improper_use, unknown_id, SocketParser

from gevent import spawn
from gevent.pool import Group
from gevent.server import StreamServer


server_logger = logging.getLogger("JesterServer")


def auto_spawn(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        s = spawn(func, self, *args, **kwargs)
        self.greenlet_group.add(s)
        return s
    return wrapper


class Cursor:

    EXPOSED = "execute", "execute_many", "execute_script"

    def __init__(self, db: sql.Connection):
        self.cursor = db.cursor()
        self.fetch_one = self.cursor.fetchone
        self.fetch_all = self.cursor.fetchall
        self.fetch_many = self.cursor.fetchmany
        self.greenlet_group = Group()

    @auto_spawn
    def execute(self, statement: str, *args):
        return self.cursor.execute(
            statement, args
        )

    @auto_spawn
    def execute_many(self, statement: str, *values):
        return self.cursor.executemany(
            statement, values
        )

    @auto_spawn
    def execute_script(self, statement: str):
        return self.cursor.executescript(statement)


class Worker(SocketParser):

    def __init__(self, conn, cursor: Cursor):
        self.cursor = cursor
        self.id = str(uuid4())
        super().__init__(conn)

    def dispatch(self, payload: dict):
        server_logger.debug("New Payload: {} | {}".format(payload, self.id))
        if 'id' not in payload:
            self.send(invalid_body)
            server_logger.warning("Received payload without ID | {}".format(self.id))
        elif payload['id'] == 0:
            if 'method' not in payload or 'statement' not in payload:
                self.send(invalid_body)
                server_logger.warning("Received execution payload without important values | {}".format(self.id))
            elif payload['method'] not in Cursor.EXPOSED:
                self.send(invalid_method)
                server_logger.warning("Received unknown execution method | {}".format(self.id))
            elif payload['method'] == 'execute_script' and 'args' in payload:
                self.send(improper_use)
                server_logger.warning("Received a payload with unsupported arguments | {}".format(self.id))
            else:
                if 'args' in payload:
                    s = getattr(self.cursor, payload['method'])(payload['statement'], *payload['args'])
                else:
                    s = getattr(self.cursor, payload['method'])(payload['statement'])
                server_logger.info("Executing '{}' | {}".format(payload['statement'], self.id))
                s.link_exception(lambda x: self.send({"id": -1, "msg": str(x.exception)}))
        elif payload['id'] == 1:
            if 'return' not in payload:
                self.send(invalid_body)
                server_logger.warning("Received request payload without return | {}".format(self.id))
            elif payload['return'] == 2 and 'size' not in payload:
                self.send(improper_use)
                server_logger.warning("Received request payload without size | {}".format(self.id))
            else:
                self.cursor.greenlet_group.join()
                if payload['return'] == 2:
                    self.send({
                        "id": 1,
                        "resp": self.cursor.fetch_many(payload.get('size', -1))
                    })
                elif payload['return'] == 1:
                    self.send({
                        "id": 1,
                        "resp": self.cursor.fetch_all()
                    })
                else:
                    self.send({
                        "id": 1,
                        "resp": self.cursor.fetch_one()
                    })
                server_logger.info("Sent requested data back to the client | {}".format(self.id))
        else:
            self.send(unknown_id)
            server_logger.warning("Received payload with unknown ID | {}".format(self.id))

    def handle_requests(self):
        server_logger.info("New Connection Established | {}".format(self.id))
        try:
            while True:
                self.dispatch(
                    self.get_payload()
                )
        except ConnectionResetError:
            pass
        server_logger.info("Connection with client finished | {}".format(self.id))


def worker_factory(db: sql.Connection, connection):
    cursor = Cursor(db)
    try:
        Worker(connection, cursor).handle_requests()
    finally:
        cursor.greenlet_group.join()
        cursor.cursor.close()
    db.commit()
    server_logger.debug("Database committed")


def start_server(host: str, port: int, file_path: str = "jester.db"):
    db = sql.connect(file_path)
    server = StreamServer((host, port), lambda x, _: worker_factory(db, x))
    server_logger.debug("Server initialized, starting.")
    server.serve_forever()


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--port', type=int, help="What port the server should listen to", default=27345)
    parser.add_argument('--host', help="What IP should we listen to", default="localhost")
    parser.add_argument('--file', help="What file should the server use as a database", default='jester.db')
    parser.add_argument("-n", "--no-logging", action="store_true", help="Disable logging")
    parser.add_argument("--level", help="Logging level", default="INFO")
    args = parser.parse_args()

    if not args.no_logging:
        logging.basicConfig()
        server_logger.setLevel(args.level)

    start_server(args.host, args.port, args.file)
