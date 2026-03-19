import os
import pytest

from resources.lib.services.provider_service import ProviderService
from resources.lib.providers.provider_base import ProviderSource


class DummyProvider:
    def search(self, title, year=None, media_type='movie'):
        return [
            ProviderSource('dummy', title, media_type, year, '1080p', 'http://source1', {}),
            ProviderSource('dummy', title, media_type, year, '720p', 'http://source2', {}),
            ProviderSource('dummy', title, media_type, year, '1080p', 'http://source1', {})
        ]


def test_provider_service_dedupe_and_quality():
    ps = ProviderService()
    ps.providers = [DummyProvider()]
    sources = ps.search_sources('test', year=2023, media_type='movie')
    assert len(sources) == 2
    best = ps.get_best_source('test', year=2023, media_type='movie')
    assert best.url == 'http://source1'
    assert best.quality == '1080p'


@pytest.mark.skipif(os.environ.get('PROVIDER_INTEGRATION') != '1',
                    reason='Provider integration requires PROVIDER_INTEGRATION=1')
def test_provider_service_real_integration_by_title():
    # Attempt to perform real provider lookup on actual sample content using Coco/Magneto provider stacks.
    # Requires `cocoscrapers` and/or `magneto` package installed.
    title = os.environ.get('SAMPLE_SHOW', 'Breaking Bad')
    ps = ProviderService()
    sources = ps.search_sources(title, media_type='show')

    assert isinstance(sources, list)
    assert sources, (
        'No sources returned. Ensure coco/magneto provider packages are installed and network access is available.'
    )
    assert any(src.url for src in sources)
