import os
from pygame.surface import Surface
from pygame.sprite import Group
from entities import Spaceship, Enemy
import pygame
import random

from UI import Stars, Button, DialogueWindow, GameDialogueWindow, Score

from config import THEME, CFG
from random import choice

from particles import BulletParticle, CursorParticle, DeathParticle, Particle, SpaceshipParticle


class State:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.bg_color = THEME.BLACK
        self.should_change_state = False
        self.next_state = None
        self.lt = 0

    def exit_cb(self):
        self.should_change_state = True
        self.next_state = TransitionStateIn(self.screen, ExitState(self.screen))

    def run(self):
        self.lt += 1

    def update(self):
        # update stuff
        pass

class DeathState(State):
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 20)
    
    prev_score = 0
    
    if not os.path.exists("score.txt"):
        with open("score.txt", "w") as f:
            try:
                f.write("0")
            except Exception as e:
                print(f"Error while parsing score file: {e}")
    
    with open("score.txt", "r") as f:
        try:
            score = f.readline()
            prev_score = int(score)
        except Exception as e:
            print(f"Error while parsing score file: {e}")

    
    def __init__(self, screen: Surface, score:int):
        super().__init__(screen)
        self.clock = pygame.time.Clock()
        self.score = score
        self.dg = None
        self.new_highscore = False
                
        if score > self.prev_score:
            with open("score.txt", "w") as f:
                try:
                    f.write(str(score))
                    self.new_highscore = True
                except Exception as e:
                    print(f"Error while parsing score file: {e}")
        
    def game_cb(self):
        self.should_change_state = True
        self.next_state = TransitionStateIn(self.screen, Level1State(self.screen))

    def exit_cb(self):
        self.should_change_state = True
        self.next_state = TransitionStateIn(self.screen, ExitState(self.screen))
    
    def menu_cb(self):
        self.should_change_state = True
        self.next_state = TransitionStateIn(self.screen, MainMenuState(self.screen))
    
    def run(self):
        game_button = Button(
            10, 220 + (48 + 10) * 0, 460, 48, self.screen, "Play again!", self.game_cb
        )
        menu_button = Button(
            10, 220 + (48 + 10) * 1, 460, 48, self.screen, "Exit to menu!", self.menu_cb
        )
        exit_button = Button(
            10, 220 + (48 + 10) * 2, 460, 48, self.screen, "Exit!", self.exit_cb
        )
        stateRunning = True
        
        score_message = None
        
        
        if self.new_highscore:
            score_message = self.my_font.render(f"!!You set your new highscore: {self.score}!!", True, THEME.WHITE)
        else:
            score_message = self.my_font.render(f"You died with score: {self.score}. Your highscore is: {self.prev_score}", True, THEME.WHITE)
        
        while stateRunning:
            self.lt += 1
            if self.should_change_state:
                return self.next_state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_cb()
            self.screen.fill(THEME.BLACK)

            self.screen.blit(score_message, score_message.get_rect(center=(self.screen.get_rect().centerx, 20)))
            game_button.update()
            menu_button.update()
            exit_button.update()
            
            
            if self.dg != None:
                self.dg.update()
                if self.dg.is_finished():
                    self.dg = None
            pygame.display.flip()
            self.clock.tick(75)
        
class Level1State(State):
    def __init__(self, sc: Surface):
        super().__init__(sc)
        self.bg_color = THEME.BLACK
        self.cheerups = {
            "Walter": [
                "SMASH INSECTOIDS!",
                "BOILED!",
                "ULTRAKILL",
                "BEAT BUGS!",
                "TASTY!",
                "DAMN!",
                "COOL!",
            ],
            "Jesse": [
                "NICE SHOT!",
                "I AM NOT GONNA CLEAN IT UP!!",
                "FOR OUR TACOS!",
                "I FORBID YOU TO EAT MY LOS TACOS!!",
                "ADVANCED AEROBATICS!",
            ],
        }
        self.dg = None

    def menu_cb(self):
        self.next_state = TransitionStateIn(self.screen, MainMenuState(self.screen))
        self.should_change_state = True

    def death_cb(self, score):
        self.next_state = TransitionStateIn(self.screen, DeathState(self.screen, score))
        self.should_change_state = True
    
    def first_cutscene(self):
        pass
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        score = Score(self.screen)

        enemyGroup = Group()
        particleGroup = Group()
        bulletGroup = Group()
        p_bulletGroup = Group()
        playerGroup = Group()
        playerGroup.add(Spaceship(CFG.WIDTH // 2, CFG.HEIGHT - 50, pt=particleGroup, bt=p_bulletGroup))

        stars = Stars(self.screen)
        
        enemyCounter = 10

        for i in range(enemyCounter):
            x, y = random.randint(0, CFG.WIDTH), random.randint(0, 300)
            en = Enemy(x, y, pt=particleGroup, bt=bulletGroup)
            enemyGroup.add(en)

        while running:
            if len(playerGroup.sprites()) == 0:
                self.death_cb(score.score)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_cb()
                if event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        self.menu_cb()

            if self.should_change_state:
                return self.next_state

            
            pygame.display.flip()
            self.screen.fill(self.bg_color)

            for enemy in enemyGroup:
                if len(playerGroup.sprites()) == 0:
                    break
                hit = pygame.sprite.spritecollide(enemy, playerGroup.sprites()[0].bullets, True)
                if hit:
                    enemy.reduce_hp(playerGroup.sprites()[0].damage)
                    score.change_score(2)

            
            pygame.sprite.groupcollide(p_bulletGroup, bulletGroup, True, True)
            
            
            for enemy in enemyGroup:
                if len(playerGroup.sprites()) == 0:
                    break
                hit = pygame.sprite.spritecollide(playerGroup.sprites()[0], enemy.bullets, True)
                if hit:
                    playerGroup.sprites()[0].reduce_hp(enemy.damage)

            
            if len(enemyGroup) < enemyCounter:
                score.change_score(10)
                enemyCounter -= 1
                if random.random() > 0.8 and self.dg == None:
                    actor = random.choice(list(self.cheerups.keys()))
                    self.dg = GameDialogueWindow(
                        self.screen,
                        f"{actor}: {random.choice(self.cheerups[actor])}"
                    )

            stars.update()
            score.update()
            bulletGroup.update(self.screen)
            p_bulletGroup.update(self.screen)
            enemyGroup.update(self.screen)
            particleGroup.update(self.screen)
            playerGroup.update(self.screen)
            if self.dg != None:
                self.dg.update()
                if self.dg.is_finished():
                    self.dg = None
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
            if self.should_change_state:
                return self.next_state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_cb()
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
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 65)


    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.clock = pygame.time.Clock()
        self.dg = None
        self.cd = 0
        self.positive = True
        self.angle = 0
        self.pos_angle = True
        self.textes = [
            "Finally Done!",
            "Dude i wanna sleep",
            "Hewwo, owo",
            "COFFFEEE",
            "Thanks Ki",
            "Thanks Rm",
            "Thanks Yan",
            "Thanks Lsh",
            "smokey :3",
            "Linux is goat",
            "Windows is goat",
            "Python is goat",
            "amongus",
            "Dued",
            "If u selp it good",
            "no Tacos: Battle for the Sky???",
            "SHOOTEMUP!",
        ]
        self.current_text = self.textes[-1]
        self.p_x = 0
        self.p_y = 0
        
    def menu_cb(self):
        self.dg = DialogueWindow(
            self.screen, "There is no actual settings at the moment, Sorry!"
        )

    def game_cb(self):
        self.should_change_state = True
        self.next_state = TransitionStateIn(self.screen, Level1State(self.screen))

    def exit_cb(self):
        self.should_change_state = True
        self.next_state = TransitionStateIn(self.screen, ExitState(self.screen))

    def update_funny_title(self):
        self.update_color_delta()
        self.update_angle()
        R, G, B = THEME.WHITE
        R = self.cd
        G = self.cd
        B = self.cd

        if G == 51 and not self.positive:
            self.current_text = choice(self.textes)

        title = self.my_font.render(self.current_text, True, (R, G, B))

        title = pygame.transform.rotate(title, self.angle)
        rect = title.get_rect()
        rect.center = (CFG.WIDTH // 2, 90)

        return (title, rect)

    def update_angle(self):
        if self.lt % 5 != 0:
            return
        if self.pos_angle:
            self.angle += 1

        if self.angle >= 10:
            self.pos_angle = False

        if not self.pos_angle:
            self.angle -= 1

        if self.angle <= -10:
            self.pos_angle = True

    def update_color_delta(self):
        if self.positive:
            self.cd += 1

        if self.cd >= THEME.WHITE[0]:
            self.positive = False

        if not self.positive:
            self.cd -= 1

        if self.cd <= 0:
            self.positive = True

    def make_particle_hell(self, particlesGroup):
        (x, y) = pygame.mouse.get_pos()
        
        if self.p_x != x or self.p_y != y:
            
            for _ in range(min(abs(self.p_x - x) + abs(self.p_y - y), 10)):
                particlesGroup.add(CursorParticle(x, y, 50))
            self.p_x = x
            self.p_y = y
        if pygame.mouse.get_pressed()[0]:
            for _ in range(10):
                particlesGroup.add(Particle(x, y, 200))

        if pygame.mouse.get_pressed()[1]:
            for _ in range(10):
                particlesGroup.add(BulletParticle(x, y, 200))
        
        if pygame.mouse.get_pressed()[2]:
            for _ in range(10):
                particlesGroup.add(DeathParticle(x, y, 200))
    
    def run(self):
        game_button = Button(
            10, 220 + (48 + 10) * 0, 460, 48, self.screen, "Play!", self.game_cb
        )
        menu_button = Button(   
            10, 220 + (48 + 10) * 1, 460, 48, self.screen, "Settings!", self.menu_cb
        )
        exit_button = Button(
            10, 220 + (48 + 10) * 2, 460, 48, self.screen, "Exit!", self.exit_cb
        )
        particlesGroup = Group()
        # scr = Score(self.screen)
        stateRunning = True
        while stateRunning:
            self.lt += 1
            if self.should_change_state:
                return self.next_state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_cb()
            self.screen.fill(THEME.BLACK)

            self.make_particle_hell(particlesGroup)
            
            particlesGroup.update(self.screen)
            game_button.update()
            menu_button.update()
            exit_button.update()
            self.screen.blit(*self.update_funny_title())
            if self.dg != None:
                self.dg.update()
                if self.dg.is_finished():
                    self.dg = None
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
