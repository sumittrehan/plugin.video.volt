import time


class SimpleCache:
    def __init__(self):
        self._store = {}

    def set(self, key, value, ttl=300):
        expires = time.time() + ttl
        self._store[key] = {'value': value, 'expires': expires}

    def get(self, key, default=None):
        record = self._store.get(key)
        if not record:
            return default

        if record['expires'] < time.time():
            self._store.pop(key, None)
            return default

        return record['value']

    def delete(self, key):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()
