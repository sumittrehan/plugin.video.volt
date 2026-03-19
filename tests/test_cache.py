import time
from resources.lib.core.cache import SimpleCache


def test_cache_set_get():
    c = SimpleCache()
    c.set('k', 'v', ttl=1)
    assert c.get('k') == 'v'


def test_cache_expire():
    c = SimpleCache()
    c.set('k', 'v', ttl=0.1)
    time.sleep(0.2)
    assert c.get('k') is None
