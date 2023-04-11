from pygame.surface import Surface
from pygame.sprite import Group
from drawables import Spaceship, Enemy
import pygame
import time

from config import THEME

class State:
    def __init__(self, screen: Surface):
        self.screen = screen
        # all resources should be initialized here
        pass

    def run(self):
        running = True
        while running:
            # do stuff
            pass

    def update(self):
        # update stuff
        pass

    def close(self):
        return TransitionState(self.screen, ExitState(screen=self.screen))


class Level1State(State):
    def __init__(self, sc: Surface):
        super().__init__(sc)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        enemyGroup = Group()
        particleGroup = Group()
        
        player = Spaceship(100, 100, pt=particleGroup)
        
        for i in range(10):
            en = Enemy(10 + 10 * i % 420, 10 + 10 * i % 300, pt=particleGroup)
            enemyGroup.add(en)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.close()
            pygame.display.flip()
            self.screen.fill(THEME.BLACK)
                    
            enemyGroup.update(self.screen)
            particleGroup.update(self.screen)
            player.update(self.screen)
            clock.tick(75)
            
class ExitState(State):
    def __init__(self, screen: Surface):
        super().__init__(screen)

    def run(self):
        # do stuff before closing
        exit(0)


class MainMenuState(State):
    def __init__(self, screen: Surface):
        super().__init__(screen)

    def run(self):
        pass

class TransitionState(State):
    def __init__(self, sc: Surface, next_state):
        super().__init__(sc)
        self.next_state = next_state
        
    def run(self):
        time.sleep(5)
        return self.next_state    
    

class STATES:
    EXIT = ExitState
    MAIN_MENU = MainMenuState
    LEVEL_1 = Level1State
    LEVEL_2 = 2
    LEVEL_3 = 3
