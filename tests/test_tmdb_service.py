import os
import pytest

from resources.lib.services.tmdb_service import TmdbService, TmdbError


def test_tmdb_no_api_key(monkeypatch):
    monkeypatch.delenv('TMDB_API_KEY', raising=False)
    ts = TmdbService(api_key='')
    with pytest.raises(TmdbError):
        ts.search_movie('Matrix')


@pytest.mark.skipif('TMDB_API_KEY' not in os.environ, reason='TMDB API tests need API key')
def test_tmdb_search_integration():
    ts = TmdbService(api_key=os.environ['TMDB_API_KEY'])
    data = ts.search_movie('Matrix', year=1999)
    assert 'results' in data
