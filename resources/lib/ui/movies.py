from urllib.parse import urlencode

from resources.lib.services.trakt_service import TraktService
from resources.lib.services.provider_service import parse_quality
from resources.lib.utils.logger import warning
from resources.lib.utils.xbmc_helpers import make_list_item, end_directory

try:
    import xbmcplugin
except ImportError:
    xbmcplugin = None

HANDLE = None
if __import__('sys').argv and len(__import__('sys').argv) > 1:
    try:
        HANDLE = int(__import__('sys').argv[1])
    except ValueError:
        HANDLE = None


def show_trending():
    t = TraktService()
    try:
        trending = t.get_trending(media_type='movies')
    except Exception as e:
        warning(f"Failed to load trending movies: {e}")
        trending = []

    for item in trending:
        movie = item.get('movie') or item
        title = movie.get('title', 'Unknown')
        year = movie.get('year')
        params = {
            'action': 'movies_play',
            'title': title,
            'year': year,
        }
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=False, info={'title': title, 'year': year})
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=False)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_recommended():
    t = TraktService()
    try:
        recs = t.get_recommendations(media_type='movies')
    except Exception as e:
        warning(f"Failed to load recommended movies: {e}")
        recs = []

    for item in recs:
        title = item.get('title', 'Unknown')
        year = item.get('year')
        params = {'action': 'movies_play', 'title': title, 'year': year}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=False, info={'title': title, 'year': year})
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=False)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def search_movies():
    # This should open text input dialog via xbmc
    try:
        import xbmcgui
    except ImportError:
        return

    kb = xbmcgui.Keyboard('', 'Search Movies')
    kb.doModal()
    if not kb.isConfirmed():
        return

    query = kb.getText()

    # using Trakt search
    t = TraktService()
    try:
        results = t.search_movies(query)
    except Exception as e:
        warning(f"Search failed: {e}")
        results = []

    for item in results:
        movie = item.get('movie', {})
        title = movie.get('title', 'Unknown')
        year = movie.get('year')
        params = {'action': 'movies_play', 'title': title, 'year': year}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=False, info={'title': title, 'year': year})
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=False)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_watchlist():
    t = TraktService()
    try:
        movies = t.get_watchlist(media_type='movies')
    except Exception as e:
        warning(f"Failed to load movie watchlist: {e}")
        movies = []

    for item in movies:
        movie = item.get('movie') or item
        title = movie.get('title', 'Unknown')
        year = movie.get('year')
        params = {'action': 'movies_play', 'title': title, 'year': year}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=True, info={'title': title, 'year': year})
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_movie_sources(tmdb_id=None, imdb_id=None, title=None, year=None, resume_seconds=0):
    from resources.lib.services.provider_service import ProviderService

    providers = ProviderService()
    sources = providers.search_sources(title=title, year=year, media_type='movie')

    if not sources:
        warning('No sources found for movie')
        return

    for src in sorted(sources, key=lambda s: parse_quality(s.quality), reverse=True):
        params = {
            'action': 'play_source',
            'source_url': src.url,
            'media_type': 'movie',
            'title': title,
            'tmdb_id': tmdb_id,
            'imdb_id': imdb_id,
            'year': year,
            'resume_seconds': resume_seconds,
        }
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        label = f"{src.provider.upper()} - {src.quality} - {src.url}"
        li = make_list_item(label, path=path, is_folder=False, info={'title': title, 'year': year})
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=False)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)
