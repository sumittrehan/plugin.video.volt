import os

from resources.lib.utils.http import HttpClient, HttpClientError
from resources.lib.utils.logger import debug, warning

TMDB_BASE = 'https://api.themoviedb.org/3'


class TmdbError(Exception):
    pass


class TmdbService:
    def __init__(self, api_key=None):
        # if api_key is explicitly provided as '', keep it as empty so is_configured() remains False
        self.api_key = api_key if api_key is not None else os.getenv('TMDB_API_KEY')
        self.http = HttpClient(timeout=15)

    def is_configured(self):
        return bool(self.api_key)

    def _request(self, path, params=None):
        if not self.is_configured():
            raise TmdbError('TMDB API key not configured')

        params = params or {}
        params['api_key'] = self.api_key

        url = f"{TMDB_BASE}/{path}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
        try:
            return self.http.request(url, method='GET')
        except HttpClientError as e:
            raise TmdbError(str(e))

    def search_movie(self, query, year=None):
        params = {'query': query}
        if year:
            params['year'] = year
        return self._request('search/movie', params=params)

    def search_show(self, query):
        return self._request('search/tv', params={'query': query})

    def get_movie_details(self, tmdb_id):
        return self._request(f'movie/{tmdb_id}')

    def get_show_details(self, tmdb_id):
        return self._request(f'tv/{tmdb_id}')
