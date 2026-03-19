from urllib.parse import urlencode

from resources.lib.services.trakt_service import TraktService
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


def _emit_items(items, media_type='movies'):
    for item in items:
        if media_type == 'shows':
            obj = item.get('show') or item
        else:
            obj = item.get('movie') or item

        title = obj.get('title', 'Unknown')
        year = obj.get('year')
        params = {'action': 'movies_play' if media_type == 'movies' else 'shows_seasons', 'title': title, 'year': year}
        path = __import__('sys').argv[0] + '?' + urlencode(params)
        li = make_list_item(title, path=path, is_folder=(media_type == 'shows'))
        if xbmcplugin and HANDLE is not None:
            xbmcplugin.addDirectoryItem(HANDLE, path, li, isFolder=(media_type == 'shows'))

    if xbmcplugin and HANDLE is not None:
        end_directory(HANDLE)


def show_widget_inprogress_movies():
    t = TraktService()
    try:
        items = t.get_continue_watching() or []
    except Exception as e:
        warning(f"Widget in-progress movies: {e}")
        items = []

    _emit_items(items, media_type='movies')


def show_widget_inprogress_shows():
    t = TraktService()
    try:
        items = t.get_continue_watching() or []
    except Exception as e:
        warning(f"Widget in-progress shows: {e}")
        items = []

    _emit_items(items, media_type='shows')


def show_widget_recommendations():
    t = TraktService()
    try:
        items = t.get_recommendations(media_type='movies') or []
    except Exception as e:
        warning(f"Widget recommendations: {e}")
        items = []

    _emit_items(items, media_type='movies')


def show_widget_trending():
    t = TraktService()
    try:
        items = t.get_trending(media_type='movies') or []
    except Exception as e:
        warning(f"Widget trending: {e}")
        items = []

    _emit_items(items, media_type='movies')


def show_widget_popular():
    t = TraktService()
    try:
        items = t.get_trending(media_type='tv') or []
    except Exception as e:
        warning(f"Widget popular: {e}")
        items = []

    _emit_items(items, media_type='shows')
