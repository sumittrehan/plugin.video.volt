from resources.lib.utils.http import HttpClient, HttpClientError
from resources.lib.utils.settings import get_setting, set_setting
from resources.lib.utils.logger import info, warning, error, debug
from resources.lib.core.cache import SimpleCache

RD_BASE = 'https://api.real-debrid.com/rest/1.0'

cache = SimpleCache()


class RealDebridError(Exception):
    pass


class RealDebridService:
    def __init__(self):
        self.token = get_setting('realdebrid_token')
        self.http = HttpClient(timeout=20)

    def is_configured(self):
        return bool(self.token)

    def authorize(self):
        # token should be set in advanced settings by user; no flow in initial scope
        if not self.token:
            raise RealDebridError('Real-Debrid token not configured')

    def unrestrict_link(self, link):
        if not self.token:
            raise RealDebridError('Real-Debrid token missing')

        cache_key = f"rd:{link}"
        cached = cache.get(cache_key)
        if cached is not None:
            debug(f"RealDebrid cache hit for {link}")
            return cached

        headers = {'Authorization': f"Bearer {self.token}"}
        try:
            result = self.http.request(f"{RD_BASE}/unrestrict/link", method='POST', headers=headers, payload={'link': link})
            if 'download' in result:
                cache.set(cache_key, result, ttl=60)
                return result
            raise RealDebridError('No download URL returned')
        except HttpClientError as e:
            raise RealDebridError(str(e))

    def get_available_hosters(self):
        try:
            result = self.http.request(f"{RD_BASE}/hosts/resolve", method='GET', headers={'Authorization': f"Bearer {self.token}"})
            return result
        except HttpClientError as e:
            raise RealDebridError(str(e))
