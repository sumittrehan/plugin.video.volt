from urllib.parse import urlencode

from resources.lib.services.trakt_service import TraktService
from resources.lib.services.provider_service import ProviderService, parse_quality
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
        trending = t.get_trending(media_type='shows')
    except Exception as e:
        warning(f"Failed to load trending shows: {e}")
        trending = []

    for item in trending:
        show = item.get('show') or item
        title = show.get('title', 'Unknown')
        year = show.get('year')
        params = {'action': 'shows_seasons', 'title': title}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=True, info={'title': title, 'year': year})
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_recommended():
    t = TraktService()
    try:
        recs = t.get_recommendations(media_type='shows')
    except Exception as e:
        warning(f"Failed to load recommended shows: {e}")
        recs = []

    for item in recs:
        title = item.get('title', 'Unknown')
        params = {'action': 'shows_seasons', 'title': title}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=True)
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_seasons(tmdb_id=None, imdb_id=None, title=None):
    t = TraktService()
    if not title:
        return

    show = t.get_show_by_title(title)
    if not show:
        warning('Show not found in Trakt')
        return

    show_id = (show.get('ids') or {}).get('trakt')
    if not show_id:
        warning('Show tramkt id not found')
        return

    seasons = t.get_show_seasons(show_id)
    for s in seasons:
        season_number = s.get('number')
        params = {'action': 'shows_episodes', 'title': title, 'season': season_number, 'tmdb_id': tmdb_id, 'imdb_id': imdb_id}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(f"Season {season_number}", path=path, is_folder=True)
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_episodes(tmdb_id=None, imdb_id=None, title=None, season=None):
    t = TraktService()
    if not title or season is None:
        return

    show = t.get_show_by_title(title)
    if not show:
        warning('Show not found in Trakt')
        return

    show_id = (show.get('ids') or {}).get('trakt')
    if not show_id:
        warning('Show trakt id not found')
        return

    episodes = t.get_show_episodes(show_id, season)
    for ep in episodes:
        ep_title = ep.get('title', f"Episode {ep.get('number')}")
        ep_number = ep.get('number')
        params = {
            'action': 'shows_play',
            'title': title,
            'season': season,
            'episode': ep_number,
            'tmdb_id': tmdb_id,
            'imdb_id': imdb_id,
        }
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(f"S{season:02}E{ep_number:02} - {ep_title}", path=path, is_folder=True)
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_episode_sources(tmdb_id=None, imdb_id=None, title=None, season=None, episode=None, resume_seconds=0):
    providers = ProviderService()
    sources = providers.search_sources(title=title, year=None, media_type='episode')

    if not sources:
        warning('No sources found for episode')
        return

    for src in sorted(sources, key=lambda s: parse_quality(s.quality), reverse=True):
        params = {
            'action': 'play_source',
            'source_url': src.url,
            'media_type': 'episode',
            'title': title,
            'tmdb_id': tmdb_id,
            'imdb_id': imdb_id,
            'season': season,
            'episode': episode,
            'resume_seconds': resume_seconds,
        }
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        label = f"{src.provider.upper()} - {src.quality} - {src.url}"
        li = make_list_item(label, path=path, is_folder=False)
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=False)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def search_shows():
    try:
        import xbmcgui
    except ImportError:
        return

    kb = xbmcgui.Keyboard('', 'Search Shows')
    kb.doModal()
    if not kb.isConfirmed():
        return

    query = kb.getText()
    t = TraktService()
    try:
        results = t.search_shows(query)
    except Exception as e:
        warning(f"Show search failed: {e}")
        results = []

    for item in results:
        show = item.get('show', {})
        title = show.get('title', 'Unknown')
        params = {'action': 'shows_seasons', 'title': title}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=True)
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_watchlist():
    t = TraktService()
    try:
        shows = t.get_watchlist(media_type='shows')
    except Exception as e:
        warning(f"Failed to load TV show watchlist: {e}")
        shows = []

    for item in shows:
        show = item.get('show') or item
        title = show.get('title', 'Unknown')
        params = {'action': 'shows_seasons', 'title': title}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=True)
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)
