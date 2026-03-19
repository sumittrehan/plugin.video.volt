from urllib.parse import urlencode

from resources.lib.services.trakt_service import TraktService
from resources.lib.utils.logger import info, warning
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


def _add_item(params, title, is_folder=True):
    plugin_url = __import__('sys').argv[0] + '?' + urlencode(params)
    li = make_list_item(title, path=plugin_url, is_folder=is_folder)
    if xbmcplugin and HANDLE is not None:
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=plugin_url, listitem=li, isFolder=is_folder)


def show_home():
    _add_item({'action': 'trakt_continue_watching'}, 'Continue Watching', is_folder=True)
    _add_item({'action': 'trakt_watchlist_movies'}, 'Trakt Watchlist Movies', is_folder=True)
    _add_item({'action': 'trakt_watchlist_shows'}, 'Trakt Watchlist TV Shows', is_folder=True)
    _add_item({'action': 'widget_trakt_recommendations'}, 'Trakt Recommendations (Widget)', is_folder=True)
    _add_item({'action': 'trakt_auth'}, 'Authenticate with Trakt', is_folder=False)
    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def _calc_resume_seconds(item):
    progress = item.get('progress')
    runtime = None

    if item.get('movie'):
        runtime = item.get('movie', {}).get('runtime')
    elif item.get('episode'):
        runtime = item.get('episode', {}).get('runtime')

    if progress is None or runtime is None:
        return 0

    try:
        runtime = int(runtime)
        return int((float(progress) / 100.0) * runtime)
    except Exception:
        return 0


def _format_time(seconds):
    try:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return '00:00:00'


def show_continue_watching():
    t = TraktService()
    try:
        progress = t.get_continue_watching() or []
    except Exception as e:
        warning(f"Failed to load continue watching: {e}")
        progress = []

    for item in progress:
        resume_seconds = _calc_resume_seconds(item)
        resume_label = ''
        if resume_seconds > 0:
            resume_label = f" (Resume { _format_time(resume_seconds) })"

        if item.get('movie'):
            movie = item.get('movie')
            title = movie.get('title', 'Unknown')
            year = movie.get('year')
            params = {
                'action': 'movies_play',
                'title': title,
                'year': year,
                'resume_seconds': resume_seconds,
            }
            path = __import__('sys').argv[0] + '?' + urlencode(params)
            li = make_list_item(f"{title}{resume_label}", path=path, is_folder=True,
                                info={'title': title, 'year': year})
        else:
            ep = item.get('episode')
            show = item.get('show')
            title = show.get('title', 'Unknown')
            label = f"{title} S{ep.get('season')}E{ep.get('number')}{resume_label}"
            params = {
                'action': 'shows_play',
                'title': title,
                'season': ep.get('season'),
                'episode': ep.get('number'),
                'resume_seconds': resume_seconds,
            }
            path = __import__('sys').argv[0] + '?' + urlencode(params)
            li = make_list_item(label, path=path, is_folder=True)

        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=True)

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)
