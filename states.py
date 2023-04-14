from pygame.surface import Surface
from pygame.sprite import Group
from entities import Spaceship, Enemy
import pygame
import time

from UI import Button, DialogueWindow

from config import THEME, CFG

class State:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.bg_color = THEME.BLACK

    def run(self):
        running = True
        while running:
            # do stuff
            pass

    def update(self):
        # update stuff
        pass

    def close(self):
        return TransitionStateIn(self.screen, ExitState(screen=self.screen))


class Level1State(State):
    def __init__(self, sc: Surface):
        super().__init__(sc)
        self.bg_color = THEME.BLACK
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
            self.screen.fill(self.bg_color)
            
            for enemy in enemyGroup:
                hit = pygame.sprite.spritecollide(enemy, player.bullets, True)
                if hit:
                    enemy.reduce_hp(player.damage)
                
            enemyGroup.update(self.screen)
            particleGroup.update(self.screen)
            player.update(self.screen)
            clock.tick(75)
        
class Level2State(State):
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
            self.screen.fill(self.bg_color)
            
            for enemy in enemyGroup:
                hit = pygame.sprite.spritecollide(enemy, player.bullets, True)
                if hit:
                    enemy.reduce_hp(player.damage)
                
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
        self.clock = pygame.time.Clock()
        
    def run(self):
        button = Button(10, 10, 460, 36, self.screen)
        dg = DialogueWindow(self.screen)
        stateRunning = True
        while stateRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return TransitionStateIn(self.screen, ExitState(self.screen))
            self.screen.fill(THEME.BLACK)
            button.update()
            dg.update()
            
            pygame.display.flip()
            self.clock.tick(75)

class TransitionStateIn(State):
    def __init__(self, sc: Surface, next_state):
        super().__init__(sc)
        self.next_state = next_state
        self.df = 0
        self.image = pygame.surface.Surface((2, 8))
        self.image.fill((THEME.YELLOW))
        self.clock = pygame.time.Clock()
        self.shouldStop = False
    def run(self):
        while not self.shouldStop:
            self.update()
        return self.next_state
    
    def update(self):
        self.df += 1
        rect = self.image.get_rect(center=(self.screen.get_rect().center))
        self.image = pygame.transform.scale_by(self.image, 1.5)
        
        self.screen.blit(self.image, rect)
        
        if self.image.get_rect().h > CFG.HEIGHT and self.image.get_rect().w > CFG.WIDTH:
            self.shouldStop = True
        
        pygame.display.flip()
        self.clock.tick(75)

class TransitionStateOut(TransitionStateIn):
    def __init__(self, sc: Surface, next_state):
        super().__init__(sc, next_state)
        self.image = pygame.surface.Surface((480, 640))
        self.image.fill((THEME.YELLOW))
        
    def run(self):
        while not self.shouldStop:
            self.update()
        return self.next_state
    
    def update(self):
        self.screen.fill(self.next_state.bg_color)
        self.df += 1
        rect = self.image.get_rect(center=(self.screen.get_rect().center))
        self.image = pygame.transform.scale_by(self.image, 0.5)
        
        self.screen.blit(self.image, rect)
        
        if self.image.get_rect().h < 10 and self.image.get_rect().w < 10:
            self.shouldStop = True
        
        pygame.display.flip()
        self.clock.tick(75)

class STATES:
    EXIT = ExitState
    MAIN_MENU = MainMenuState
    LEVEL_1 = Level1State
    LEVEL_2 = 2
    LEVEL_3 = 3
