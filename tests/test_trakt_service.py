import os
import time
import pytest

from resources.lib.services.trakt_service import TraktService, TraktError


def test_trakt_unauthorized():
    tt = TraktService()
    tt.client_id = ''
    tt.client_secret = ''
    with pytest.raises(TraktError):
        tt._ensure_token()


@pytest.mark.skipif(os.environ.get('TRAKT_INTEGRATION') != '1',
                    reason='Explicit Trakt integration run required')
@pytest.mark.skipif('TRAKT_CLIENT_ID' not in os.environ or 'TRAKT_CLIENT_SECRET' not in os.environ,
                    reason='Integration tests require Trakt credentials')
@pytest.mark.skipif('TRAKT_ACCESS_TOKEN' not in os.environ or 'TRAKT_REFRESH_TOKEN' not in os.environ,
                    reason='Trakt API integration requires existing tokens to avoid interactive device auth')
def test_trakt_api_integration():
    tt = TraktService()
    tt.client_id = os.environ['TRAKT_CLIENT_ID']
    tt.client_secret = os.environ['TRAKT_CLIENT_SECRET']

    tt.access_token = os.environ['TRAKT_ACCESS_TOKEN']
    tt.refresh_token = os.environ['TRAKT_REFRESH_TOKEN']
    tt.expires_at = float(os.environ.get('TRAKT_TOKEN_EXPIRES', str(time.time() + 3600)))

    trending = tt.get_trending('movies')
    assert isinstance(trending, list)
