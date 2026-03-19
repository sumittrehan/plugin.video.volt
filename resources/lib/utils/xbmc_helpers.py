try:
    import xbmc
    import xbmcgui
    import xbmcplugin
except ImportError:
    xbmc = xbmcgui = xbmcplugin = None


def make_list_item(title, path=None, is_folder=True, info=None, art=None, properties=None, resume=False):
    if xbmcgui:
        li = xbmcgui.ListItem(label=title)
        if info:
            li.setInfo('video', info)
        if art:
            li.setArt(art)
        if properties:
            for key, value in properties.items():
                li.setProperty(key, str(value))
        if not is_folder:
            li.setProperty('IsPlayable', 'true')
            li.setProperty('IsFolder', 'false')
            if resume:
                li.setProperty('ResumeTime', str(resume.get('position', 0)))
                li.setProperty('TotalTime', str(resume.get('duration', 0)))
        return li
    return None


def end_directory(handle, succeeded=True):
    if xbmcplugin:
        xbmcplugin.endOfDirectory(handle, succeeded)
