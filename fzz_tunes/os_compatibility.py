import sys

try:
    import curses
except ImportError:
    if sys.platform.startswith('win'):
        import windows_curses as curses
    else:
        raise ImportError("Curses not available on this platform")

