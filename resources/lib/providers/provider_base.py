class ProviderSource:
    def __init__(self, provider, title, media_type, year, quality, url, info=None):
        self.provider = provider
        self.title = title
        self.media_type = media_type
        self.year = year
        self.quality = quality
        self.url = url
        self.info = info or {}

    def as_dict(self):
        return {
            'provider': self.provider,
            'title': self.title,
            'media_type': self.media_type,
            'year': self.year,
            'quality': self.quality,
            'url': self.url,
            'info': self.info,
        }


class ProviderBase:
    def search(self, title, year=None, media_type='movie'):
        """Return list of ProviderSource"""
        raise NotImplementedError

    def supports_media_type(self, media_type):
        return True

