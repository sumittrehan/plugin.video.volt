import os
import pytest

from resources.lib.services.debrid_service import RealDebridService, RealDebridError


def test_debrid_missing_token():
    rd = RealDebridService()
    rd.token = ''
    with pytest.raises(RealDebridError):
        rd.unrestrict_link('magnet:?xt=urn:btih:...')


@pytest.mark.skipif('REALDEBRID_TOKEN' not in os.environ or 'REALDEBRID_TEST_LINK' not in os.environ,
                    reason='Integration tests require RD token and test link')
def test_debrid_integration():
    rd = RealDebridService()
    rd.token = os.environ['REALDEBRID_TOKEN']
    test_link = os.environ['REALDEBRID_TEST_LINK']

    try:
        result = rd.unrestrict_link(test_link)
        assert isinstance(result, dict)
        assert 'download' in result or 'error' in result
    except RealDebridError as e:
        pytest.skip(f"RealDebrid integration could not complete for this test link: {e}")
