"""
A cache module for tyrion
"""

_MASTER_CACHE = {}

class Cache(object):
    def __init__(self, namespace):
        if namespace not in _MASTER_CACHE:
            _MASTER_CACHE[namespace] = {}
        self.cache = _MASTER_CACHE[namespace]
        self.namespace = namespace

    def retrieve(self, key):
        return self.cache.get(key).copy()

    def store(self, key, value):
        self.cache[key] = value.copy()

    def clear(self):
        _MASTER_CACHE[self.namespace] = {}
        self.cache = _MASTER_CACHE[self.namespace]
