try:
    import xbmc
except ImportError:
    xbmc = None


def log(level, msg):
    text = f"[Volt] {msg}"
    if xbmc:
        xbmc.log(text, level)
    else:
        print(f"LOG[{level}]: {text}")


def debug(msg):
    log(0, msg)


def info(msg):
    log(1, msg)


def warning(msg):
    log(2, msg)


def error(msg):
    log(3, msg)
