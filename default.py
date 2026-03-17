import sys
from urllib.parse import parse_qsl, urlencode, urlparse

# Kodi handle — required for all plugin operations
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]


def build_url(params):
    """Build a plugin:// URL with given parameters"""
    return BASE_URL + '?' + urlencode(params)


def router(params):
    """
    Central router — every action in Volt passes through here.
    params is a dict of URL parameters.
    """

    action = params.get('action', 'home')

    # ── Home Screen ──────────────────────────────────────────
    if action == 'home':
        from resources.lib.ui.home import show_home
        show_home()

    # ── Movies ───────────────────────────────────────────────
    elif action == 'movies_trending':
        from resources.lib.ui.movies import show_trending
        show_trending()

    elif action == 'movies_recommended':
        from resources.lib.ui.movies import show_recommended
        show_recommended()

    elif action == 'movies_search':
        from resources.lib.ui.movies import search_movies
        search_movies()

    elif action == 'movies_play':
        from resources.lib.ui.player import play_movie
        play_movie(
            tmdb_id=params.get('tmdb_id'),
            imdb_id=params.get('imdb_id'),
            title=params.get('title'),
            year=params.get('year')
        )

    # ── TV Shows ─────────────────────────────────────────────
    elif action == 'shows_trending':
        from resources.lib.ui.shows import show_trending
        show_trending()

    elif action == 'shows_recommended':
        from resources.lib.ui.shows import show_recommended
        show_recommended()

    elif action == 'shows_search':
        from resources.lib.ui.shows import search_shows
        search_shows()

    elif action == 'shows_seasons':
        from resources.lib.ui.shows import show_seasons
        show_seasons(
            tmdb_id=params.get('tmdb_id'),
            imdb_id=params.get('imdb_id'),
            title=params.get('title')
        )

    elif action == 'shows_episodes':
        from resources.lib.ui.shows import show_episodes
        show_episodes(
            tmdb_id=params.get('tmdb_id'),
            imdb_id=params.get('imdb_id'),
            title=params.get('title'),
            season=params.get('season')
        )

    elif action == 'shows_play':
        from resources.lib.ui.player import play_episode
        play_episode(
            tmdb_id=params.get('tmdb_id'),
            imdb_id=params.get('imdb_id'),
            title=params.get('title'),
            season=params.get('season'),
            episode=params.get('episode')
        )

    # ── Trakt ────────────────────────────────────────────────
    elif action == 'trakt_watchlist_movies':
        from resources.lib.ui.movies import show_watchlist
        show_watchlist()

    elif action == 'trakt_watchlist_shows':
        from resources.lib.ui.shows import show_watchlist
        show_watchlist()

    elif action == 'trakt_continue_watching':
        from resources.lib.ui.home import show_continue_watching
        show_continue_watching()

    elif action == 'trakt_auth':
        from resources.lib.services.trakt import TraktService
        TraktService().authenticate()

    # ── Settings ─────────────────────────────────────────────
    elif action == 'open_settings':
        import xbmcaddon
        xbmcaddon.Addon().openSettings()

    # ── Unknown action ───────────────────────────────────────
    else:
        import xbmcgui
        xbmcgui.Dialog().notification(
            'Volt',
            f'Unknown action: {action}',
            xbmcgui.NOTIFICATION_WARNING,
            3000
        )


# ── Entry Point ──────────────────────────────────────────────────
if _name_ == '_main_':
    # Parse URL parameters and route
    params = dict(parse_qsl(urlparse(sys.argv[2]).query))
    router(params)
