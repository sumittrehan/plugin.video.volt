import concurrent.futures

from resources.lib.providers.coco import CocoProvider
from resources.lib.providers.magneto import MagnetoProvider
from resources.lib.providers.provider_base import ProviderSource
from resources.lib.utils.logger import debug, warning

QUALITY_RANK = {
    '4k': 5,
    '2160p': 5,
    '1080p': 4,
    '720p': 3,
    'sd': 1,
    'unknown': 0,
}


def parse_quality(quality):
    if not quality:
        return 0
    q = str(quality).lower()
    for token, rank in QUALITY_RANK.items():
        if token in q:
            return rank
    try:
        return int(q)
    except Exception:
        return 0


class ProviderService:
    def __init__(self):
        self.providers = [CocoProvider(), MagnetoProvider()]

    def search_sources(self, title, year=None, media_type='movie'):
        results = []

        def invoke(provider):
            try:
                return provider.search(title, year=year, media_type=media_type)
            except Exception as e:
                warning(f"Provider {provider.__class__.__name__} failed: {e}")
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {executor.submit(invoke, p): p for p in self.providers}
            for future in concurrent.futures.as_completed(future_map):
                provider = future_map[future]
                try:
                    data = future.result(timeout=10)
                    if data:
                        results.extend(data)
                except Exception as e:
                    warning(f"Provider {provider.__class__.__name__} yielded exception: {e}")

        # dedupe by URL; keep higher quality if duplicate
        unique = {}
        for source in results:
            key = source.url
            if key not in unique:
                unique[key] = source
            else:
                existing = unique[key]
                if parse_quality(source.quality) > parse_quality(existing.quality):
                    unique[key] = source

        resolved = list(unique.values())
        debug(f"ProviderService resolved {len(resolved)} unique sources")
        return resolved

    def get_best_source(self, title, year=None, media_type='movie'):
        sources = self.search_sources(title, year=year, media_type=media_type)
        if not sources:
            return None

        sorted_sources = sorted(sources, key=lambda s: parse_quality(s.quality), reverse=True)
        return sorted_sources[0]

