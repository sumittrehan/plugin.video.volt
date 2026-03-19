try:
    import xbmcaddon
except ImportError:
    xbmcaddon = None


ADDON_ID = 'plugin.video.volt'


def _addon():
    if xbmcaddon:
        return xbmcaddon.Addon(id=ADDON_ID)
    return None


def get_setting(key, default=''):
    addon = _addon()
    if not addon:
        return default

    try:
        value = addon.getSetting(key)
    except Exception:
        return default

    return value if value else default


def set_setting(key, value):
    addon = _addon()
    if not addon:
        return

    try:
        addon.setSetting(key, str(value))
    except Exception:
        pass
