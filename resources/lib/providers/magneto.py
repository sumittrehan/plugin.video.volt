from resources.lib.providers.provider_base import ProviderBase, ProviderSource
from resources.lib.utils.logger import debug, warning
from resources.lib.utils.settings import get_setting


class MagnetoProvider(ProviderBase):
    def __init__(self):
        self.name = 'magneto'
        self.enabled = get_setting('provider_magneto_enabled', 'true') == 'true'

    def supports_media_type(self, media_type):
        return self.enabled and media_type in ['movie', 'episode', 'show']

    def search(self, title, year=None, media_type='movie'):
        if not self.enabled:
            return []

        debug(f"MagnetoProvider.search title={title} year={year} media_type={media_type}")
        try:
            import magneto
        except ImportError:
            try:
                from resources.lib.providers import magneto_scraper as magneto
            except ImportError:
                warning('magneto module not installed')
                return []

        results = []
        try:
            query = f"{title} {year or ''}".strip()
            data = magneto.search(query)
            for entry in data:
                url = entry.get('url') or entry.get('magnet')
                if not url:
                    continue

                quality = entry.get('quality') or entry.get('resolution') or 'unknown'
                results.append(ProviderSource(
                    provider=self.name,
                    title=title,
                    media_type=media_type,
                    year=year,
                    quality=quality,
                    url=url,
                    info={
                        'source_title': entry.get('title'),
                        'size': entry.get('size'),
                        'language': entry.get('language'),
                    }
                ))
        except Exception as e:
            warning(f"MagnetoProvider search failed: {e}")

        return results
