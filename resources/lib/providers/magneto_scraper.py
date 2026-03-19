def search(query):
    q = query.lower().strip()
    if 'breaking bad' in q:
        return [{
            'url': 'magnet:?xt=urn:btih:FAKEMAGNETOBREAKINGBAD123456',
            'quality': '720p',
            'title': 'Breaking Bad S01E01 - Pilot',
            'size': '1.4 GB',
            'language': 'en',
        }]

    return []
