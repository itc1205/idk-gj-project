from config import CFG

from pygame import Surface, display


def init_window() -> Surface:
    display.set_caption(CFG.TITLE)
    return display.set_mode(CFG.WINDOW_SIZE)
