from zlib import compressobj, decompressobj, Z_SYNC_FLUSH

from msgpack import packb, unpackb


invalid_body = {
    "id": -1,
    "msg": "The message body provided was invalid"
}

invalid_method = {
    "id": -1,
    "msg": "Attempted to use non-exposed method"
}

improper_use = {
    "id": -1,
    "msg": "Method used improperly"
}

unknown_id = {
    "id": -1,
    "msg": "Unknown command ID"
}


class SocketParser:

    ZLIB_SUFFIX = b'\x00\x00\xff\xff'

    def __init__(self, conn):
        self.conn = conn
        self._buff = bytearray()
        self._comp = compressobj()
        self._infl = decompressobj()

    def send(self, payload: dict):
        payload = packb(payload)
        data = self._comp.compress(payload) + self._comp.flush(Z_SYNC_FLUSH)
        self.conn.send(data)

    def get_payload(self):
        while True:
            if b"\x00\x00\xFF\xFF" in self._buff:
                data, *self._buff = self._buff.split(b"\x00\x00\xFF\xFF")
                self._buff = bytearray(b"\x00\x00\xFF\xFF".join(self._buff))

                payload = self._infl.decompress(data + b"\x00\x00\xFF\xFF") + self._infl.flush(Z_SYNC_FLUSH)
                payload = unpackb(payload, raw=False)
                return payload
            else:
                data = self.conn.recv(64)
                if not data:
                    raise ConnectionResetError
                self._buff.extend(
                    data
                )
