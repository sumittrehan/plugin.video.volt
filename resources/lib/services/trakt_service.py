import base64
import time

from resources.lib.utils.http import HttpClient, HttpClientError
from resources.lib.utils.settings import get_setting, set_setting
from resources.lib.utils.logger import debug, info, warning, error
from resources.lib.core.cache import SimpleCache


TRAKT_BASE = 'https://api.trakt.tv'
TRAKT_TOKEN_URL = 'https://api.trakt.tv/oauth/token'
TRAKT_PIN_URL = 'https://api.trakt.tv/oauth/device/code'

cache = SimpleCache()


class TraktError(Exception):
    pass


class TraktService:
    def __init__(self):
        self.client_id = get_setting('trakt_client_id')
        self.client_secret = get_setting('trakt_client_secret')
        self.access_token = get_setting('trakt_access_token')
        self.refresh_token = get_setting('trakt_refresh_token')
        self.expires_at = float(get_setting('trakt_token_expires', '0'))
        self.http = HttpClient(timeout=15)

    def is_authorized(self):
        return bool(self.access_token and self.refresh_token and self.expires_at > time.time())

    def _save_token(self, data):
        self.access_token = data.get('access_token')
        self.refresh_token = data.get('refresh_token')
        self.expires_at = time.time() + data.get('expires_in', 0)

        set_setting('trakt_access_token', self.access_token or '')
        set_setting('trakt_refresh_token', self.refresh_token or '')
        set_setting('trakt_token_expires', str(self.expires_at))

    def _headers(self, extra=None):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': self.client_id,
        }

        if self.is_authorized():
            headers['Authorization'] = f"Bearer {self.access_token}"

        if extra:
            headers.update(extra)

        return headers

    def authenticate(self):
        if not self.client_id or not self.client_secret:
            raise TraktError('trakt_client_id and trakt_client_secret must be configured in settings')

        pin_info = self.http.request(
            TRAKT_PIN_URL,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'trakt-api-version': '2',
                'trakt-api-key': self.client_id,
            },
            payload={
                'client_id': self.client_id,
            }
        )

        device_code = pin_info.get('device_code')
        user_code = pin_info.get('user_code')
        verification_url = pin_info.get('verification_url')
        interval = pin_info.get('interval', 5)

        info(f"Trakt user code: {user_code} -> {verification_url}")

        token_payload = {
            'code': device_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        # Poll for token (shorter by default to avoid long test hangs)
        for _ in range(20):
            try:
                token = self.http.request(
                    TRAKT_TOKEN_URL,
                    method='POST',
                    payload=token_payload
                )
                if 'access_token' in token:
                    self._save_token(token)
                    info('Trakt authentication complete')
                    return token
            except HttpClientError as e:
                debug(f"Trakt polling: {e}")

            time.sleep(interval)

        raise TraktError('Trakt authentication timeout')

    def _ensure_token(self):
        if self.is_authorized():
            return

        if self.refresh_token and self.client_id and self.client_secret:
            # refresh
            payload = {
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                'grant_type': 'refresh_token',
            }
            try:
                token = self.http.request(TRAKT_TOKEN_URL, method='POST', payload=payload)
                self._save_token(token)
                return
            except HttpClientError as e:
                warning(f"Trakt refresh failed: {e}")

        raise TraktError('Trakt not authorized')

    def _get(self, path, params=None, cache_ttl=300):
        if not self.client_id:
            raise TraktError('Trakt client_id not configured')

        cache_key = f"trakt:{path}:{params}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        self._ensure_token()

        url = f"{TRAKT_BASE}/{path}"
        headers = self._headers()

        try:
            result = self.http.request(url, method='GET', headers=headers, payload=None)
        except HttpClientError as e:
            raise TraktError(str(e))

        cache.set(cache_key, result, ttl=cache_ttl)
        return result

    def get_continue_watching(self):
        return self._get('sync/playback', cache_ttl=120)

    def get_watchlist(self, media_type='movies'):
        if media_type not in ['movies', 'shows']:
            raise ValueError('media_type must be movies or shows')
        return self._get(f'sync/watchlist/{media_type}', cache_ttl=120)

    def get_recommendations(self, media_type='movies'):
        if media_type not in ['movies', 'shows']:
            raise ValueError('media_type must be movies or shows')
        return self._get(f'recommendations/{media_type}', cache_ttl=600)

    def search_movies(self, query):
        return self._get(f"search/movie?query={query}", cache_ttl=300)

    def search_shows(self, query):
        return self._get(f"search/show?query={query}", cache_ttl=300)

    def mark_watched(self, media_type, tmdb_id=None, imdb_id=None, season=None, episode=None):
        self._ensure_token()

        if media_type not in ['movie', 'episode']:
            raise ValueError('media_type must be movie or episode')

        data = {'id': {}}
        if tmdb_id:
            data['id']['tmdb'] = int(tmdb_id)
        if imdb_id:
            data['id']['imdb'] = imdb_id

        payload = {'movies': []} if media_type == 'movie' else {'episodes': []}
        if media_type == 'movie':
            payload = {'movies': [data]}
        else:
            payload = {'episodes': [{
                'ids': data['id'],
                'season': int(season) if season is not None else 1,
                'number': int(episode) if episode is not None else 1,
            }]}

        url = f"{TRAKT_BASE}/sync/history"
        headers = self._headers()

        try:
            return self.http.request(url, method='POST', headers=headers, payload=payload)
        except HttpClientError as e:
            raise TraktError(str(e))

    def get_trending(self, media_type='movies'):
        if media_type not in ['movies', 'shows']:
            raise ValueError('media_type must be movies or shows')
        return self._get(f'{media_type}/trending', cache_ttl=600)

    def get_show_by_title(self, title):
        shows = self.search_shows(title)
        if not shows:
            return None
        return shows[0].get('show') or shows[0]

    def get_show_seasons(self, show_id):
        return self._get(f'shows/{show_id}/seasons', cache_ttl=3600)

    def get_show_episodes(self, show_id, season):
        return self._get(f'shows/{show_id}/seasons/{season}/episodes', cache_ttl=3600)

    def scrobble(self, action, media_type, tmdb_id=None, imdb_id=None, title=None, year=None,
                 season=None, episode=None, progress=None, duration=None):
        self._ensure_token()

        if action not in ['start', 'pause', 'stop']:
            raise ValueError('action must be start, pause, or stop')

        if media_type not in ['movie', 'episode']:
            raise ValueError('media_type must be movie or episode')

        payload = {
            'progress': progress or 0,
            'app_version': '1.0',
            'app_date': '20250101',
        }

        if media_type == 'movie':
            payload['movie'] = {
                'ids': {
                    'tmdb': int(tmdb_id) if tmdb_id else None,
                    'imdb': imdb_id,
                }
            }
        else:
            payload['episode'] = {
                'season': int(season) if season is not None else 1,
                'number': int(episode) if episode is not None else 1,
                'ids': {
                    'tmdb': int(tmdb_id) if tmdb_id else None,
                    'imdb': imdb_id,
                }
            }

        if action == 'start':
            payload['progress'] = 0
        elif action == 'pause':
            payload['progress'] = progress or 0
        elif action == 'stop':
            payload['progress'] = progress or 100

        url = f"{TRAKT_BASE}/scrobble"
        headers = self._headers()

        try:
            result = self.http.request(url, method='POST', headers=headers, payload=payload)
            return result
        except HttpClientError as e:
            raise TraktError(str(e))
