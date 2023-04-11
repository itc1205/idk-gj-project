class CFG:
    WIDTH = 480
    HEIGHT = 640
    TITLE = "SHOOTEMUP!"
    WINDOW_SIZE = (WIDTH, HEIGHT)


class THEME:
    WHITE = (230, 234, 235)
    BLACK = (47, 51, 54)
    YELLOW = (251, 229, 172)
    RED = (255, 105, 97)
    GREEN = (139, 172, 15)


class FORMULAS:
    NORMALIZE_ALPHA = lambda x: x % 255
    P_DEATH = lambda lt, dt: FORMULAS.NORMALIZE_ALPHA(lt + dt)
    E_MOVEMENT = lambda x, y: ()
