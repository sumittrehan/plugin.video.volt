from resources.lib.services.provider_service import ProviderService
from resources.lib.services.debrid_service import RealDebridService, RealDebridError
from resources.lib.services.trakt_service import TraktService, TraktError
from resources.lib.utils.logger import info, warning, error

try:
    import xbmc
    import xbmcgui
except ImportError:
    xbmc = None
    xbmcgui = None


def _play_stream(stream_url, title):
    if xbmc and xbmcgui:
        item = xbmcgui.ListItem(path=stream_url)
        item.setInfo('video', {'title': title})
        xbmc.Player().play(stream_url, item)
    else:
        info(f"play stream: {title} -> {stream_url}")


def _resolve_debrid(url):
    rd = RealDebridService()
    if rd.is_configured():
        try:
            data = rd.unrestrict_link(url)
            return data.get('download') or url
        except RealDebridError as e:
            warning(f"RealDebrid resolve failed: {e}")
            return url
    return url


def _scrobble(action, media_type, tmdb_id=None, imdb_id=None, title=None, year=None,
              season=None, episode=None, progress=None):
    try:
        t = TraktService()
        t.scrobble(action, media_type, tmdb_id=tmdb_id, imdb_id=imdb_id,
                   title=title, year=year, season=season, episode=episode, progress=progress)
    except TraktError as e:
        warning(f"Trakt scrobble {action} failed: {e}")


def _format_time(seconds):
    try:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return '00:00:00'


def play_source(source_url, media_type, title=None, tmdb_id=None, imdb_id=None,
                year=None, season=None, episode=None, resume_seconds=0):
    if not source_url:
        warning('No source URL provided')
        return

    resolved = _resolve_debrid(source_url)
    label = title or 'Unknown'
    if media_type == 'episode':
        label = f"{title} S{season}E{episode}" if title else label

    if xbmc and xbmcgui and resume_seconds > 0:
        readable = _format_time(resume_seconds)
        proceed = xbmcgui.Dialog().yesno('Volt', f'Resume from {readable}?')
        _play_stream(resolved, label)
        if proceed:
            try:
                player = xbmc.Player()
                player.seekTime(resume_seconds)
            except Exception as e:
                warning(f'Unable to seek to resume point: {e}')
    else:
        _play_stream(resolved, label)

    _scrobble('start', media_type, tmdb_id=tmdb_id, imdb_id=imdb_id,
              title=title, year=year, season=season, episode=episode, progress=0)


def play_movie_direct(tmdb_id=None, imdb_id=None, title=None, year=None):
    prov = ProviderService()
    best = prov.get_best_source(title=title, year=year, media_type='movie')
    if not best:
        warning('No provider source found for movie')
        return

    play_source(best.url, 'movie', title=title, tmdb_id=tmdb_id, imdb_id=imdb_id, year=year)


def play_episode_direct(tmdb_id=None, imdb_id=None, title=None, season=None, episode=None):
    prov = ProviderService()
    best = prov.get_best_source(title=title, media_type='episode')
    if not best:
        warning('No provider source found for episode')
        return

    play_source(best.url, 'episode', title=title, tmdb_id=tmdb_id,
                imdb_id=imdb_id, season=season, episode=episode)

