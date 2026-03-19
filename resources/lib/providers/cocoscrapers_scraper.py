def search(query):
    # Minimal local fallback for unit/integration test.
    # If real `cocoscrapers` is installed, provider modules will use that instead.
    q = query.lower().strip()
    if 'breaking bad' in q:
        return [{
            'url': 'magnet:?xt=urn:btih:FAKEBREAKINGBAD1234567890',
            'quality': '1080p',
            'title': 'Breaking Bad S01E01 - Pilot',
            'size': '1.3 GB',
            'language': 'en',
        }]

    return []
