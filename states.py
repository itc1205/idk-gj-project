import os
from pygame.surface import Surface
from pygame.sprite import Group
from entities import Boss, FastEnemy, PowerUPs, ShitEnemy, SlowEnemy, Spaceship, Enemy
import pygame
import random

from UI import BossHealth, Health, Stars, Button, DialogueWindow, GameDialogueWindow, Score, CutsceneDialogueWindow

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

class FirstCutscene(State):
    
    def __init__(self, screen: Surface):
        super().__init__(screen)
        
        self.wt = 0
        self.WAIT_TIME = 75
        self.dialogues = [
            CutsceneDialogueWindow(self.screen, "Damn i really love sleeping ;333"),
            CutsceneDialogueWindow(self.screen, "I am just a silly sleeper ;333"),
            CutsceneDialogueWindow(self.screen, "Anyways lets get back to the game."),
            CutsceneDialogueWindow(self.screen, "The Earth was invaded by Spacebugs, their main aim is - Tacos recipe. For protecting the planet from aliens, handsome AAC's (Air Anomalous Coalitions) colonel-general Mario Velocity, lieutenant Zick Rivera was chosen to fight with bugs. As companions he's got private Walter and sergeant Jesse. Together, they should accept battle and arm by Dichlorvos."),
            CutsceneDialogueWindow(self.screen, "BAC: 'The city is under attack! That's not a usual event! That's Bugs from Space'"),
            CutsceneDialogueWindow(self.screen, "MARIO: 'Ustedes, are you ready? We're starting for Tres... Dos... Uno!.. See ya!'")
        ]
        self.next_state = TransitionStateIn(self.screen, Level1State(self.screen))
    def next_level_cb(self):
        self.should_change_state = True
    
    def run(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/csamb1.wav")
        pygame.mixer.music.play(1)
        running = True
        clock = pygame.time.Clock()
        
        
        stars = Stars(self.screen)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_cb()
                if event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_SPACE]:
                        self.next_level_cb()                        
                    
            if self.should_change_state:
                return self.next_state

            if self.dialogues[0].is_finished():
                if self.wt < self.WAIT_TIME:
                    self.wt += 1
                else:
                    self.dialogues.pop(0)
                    self.wt = 0
            
            if len(self.dialogues) <= 0:
                self.next_level_cb()
                continue
            self.screen.fill(THEME.BLACK)
            stars.update()
            self.dialogues[0].update()
            pygame.display.flip()
            clock.tick(75)        

class SecondCutscene(FirstCutscene):
    def __init__(self, screen: Surface, score):
        super().__init__(screen)
        self.score = score
        self.dialogues = [
            CutsceneDialogueWindow(self.screen, "Unknown creature: 'Bzz... It's working? Bzz, never mind. You have never been able to defeat GREAT BAB! MY HORNS MUCH BIGGER THAN YOURS! FEEL THEIR POWER ON YOUR LIPS!!!!'"),
        ]
        self.next_state = TransitionStateIn(self.screen, Level2State(self.screen, self.score))

class DeathState(State):
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 20)
    
    

    
    def __init__(self, screen: Surface, score: int):
        super().__init__(screen)
        
        self.prev_score = 0
    
        if not os.path.exists("score.txt"):
            with open("score.txt", "w") as f:
                try:
                    f.write("0")
                except Exception as e:
                    print(f"Error while parsing score file: {e}")

        with open("score.txt", "r") as f:
            try:
                prev_score = int(f.readline())
            except Exception as e:
                print(f"Error while parsing score file: {e}")
            
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
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/vi sdohli.wav")
        pygame.mixer.music.play(1)
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
        self.enemy_dmg = 10
        self.bg_color = THEME.BLACK
        self.cheerups = {
            "Walter": [
                "SMASH THOSE INSECTOIDS!",
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
        self.score = Score(self.screen)
        self.dt = 0
    def menu_cb(self):
        self.next_state = TransitionStateIn(self.screen, MainMenuState(self.screen))
        self.should_change_state = True

    def death_cb(self, score: int):
        self.next_state = TransitionStateIn(self.screen, DeathState(self.screen, score))
        self.should_change_state = True
    
    def boss_level_cb(self, score):
        self.next_state = TransitionStateIn(self.screen, SecondCutscene(self.screen, score))
        self.should_change_state = True
    
    def add_enemy_wave_1(self, enemyGroup, particleGroup, bulletGroup, powerUpGroup, N=10):
        
        for i in range(N):
            x, y = random.randint(40, CFG.WIDTH - 40), random.randint(40, 300)
            en = Enemy(x, y, pt=particleGroup, bt=bulletGroup, pu=powerUpGroup)
            enemyGroup.add(en)
            
    def add_enemy_wave_2(self, enemyGroup, particleGroup, bulletGroup, powerUpGroup, N=15):
        enemies = [Enemy, SlowEnemy]
        
        for i in range(N):
            x, y = random.randint(40, CFG.WIDTH - 40), random.randint(40, 300)
            en = choice(enemies)(x, y, pt=particleGroup, bt=bulletGroup, pu=powerUpGroup)
            enemyGroup.add(en)
    def add_enemy_wave_3(self, enemyGroup, particleGroup, bulletGroup, powerUpGroup, N=10):
        enemies = [FastEnemy]
        
        for i in range(N):
            x, y = random.randint(40, CFG.WIDTH - 40), random.randint(40, 300)
            en = choice(enemies)(x, y, pt=particleGroup, bt=bulletGroup, pu=powerUpGroup)
            enemyGroup.add(en)
            
    def add_enemy_wave_4(self, enemyGroup, particleGroup, bulletGroup, powerUpGroup, N=20):
        enemies = [Enemy, SlowEnemy, FastEnemy, ShitEnemy]
        
        for i in range(N):
            x, y = random.randint(40, CFG.WIDTH - 40), random.randint(40, 300)
            en = choice(enemies)(x, y, pt=particleGroup, bt=bulletGroup, pu=powerUpGroup)
            enemyGroup.add(en)
    def check_if_enemy_got_hit(self, enemyGroup, playerGroup):
        for enemy in enemyGroup:
            if len(playerGroup.sprites()) == 0:
                break
            hit = pygame.sprite.spritecollide(enemy, playerGroup.sprites()[0].bullets, True)
            if hit:
                enemy.reduce_hp(playerGroup.sprites()[0].damage)
                self.score.change_score(2)
    
    def check_if_bullets_got_hit(self, p_bulletGroup, bulletGroup):
        pygame.sprite.groupcollide(p_bulletGroup, bulletGroup, True, True)
    
    def check_if_player_got_hit(self, playerGroup, bulletGroup, dmg):
        
        for bullet in bulletGroup:
            if len(playerGroup.sprites()) == 0:
                return
            hit = pygame.sprite.collide_rect(bullet, playerGroup.sprites()[0])
            
            if hit:
                playerGroup.sprites()[0].reduce_hp(bullet.damage)
                bullet.die()
    def check_if_player_got_powerup(self, playerGroup: Group, powerUpGroup: Group, enemyGroup: Group):
        
        for powerUp in powerUpGroup:
            hit = pygame.sprite.collide_rect(powerUp, playerGroup.sprites()[0])
            if hit:
                
                if powerUp.type == PowerUPs.HEAL:
                    #print("the fuck")
                    playerGroup.sprites()[0].hp = min(playerGroup.sprites()[0].hp + 50, 200)
                elif powerUp.type == PowerUPs.POINTS:
                    self.score.score += 100
                elif powerUp.type == PowerUPs.KILL_ALL:
                    for enemy in enemyGroup:
                        enemy.die()
                powerUp.die()
    
    def run(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/themep.wav")
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(1)
        waves = [
            self.add_enemy_wave_1,
            self.add_enemy_wave_2,
            self.add_enemy_wave_3,
            self.add_enemy_wave_4
        ]
        nums_of_enemies = [
            10,
            20,
            15,
            20
        ]
        clock = pygame.time.Clock()
        running = True

        enemyGroup = Group()
        particleGroup = Group()
        bulletGroup = Group()
        p_bulletGroup = Group()
        playerGroup = Group()
        powerUpGroup = Group()
        playerGroup.add(Spaceship(CFG.WIDTH // 2, CFG.HEIGHT - 50, pt=particleGroup, bt=p_bulletGroup))
        
        hp = Health(self.screen, playerGroup.sprites()[0].hp, playerGroup.sprites()[0].hp) # type: ignore
        stars = Stars(self.screen)
        
        enemyCounter = 10
        
        while running:
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

            self.check_if_enemy_got_hit(enemyGroup, playerGroup)

            pygame.sprite.groupcollide(p_bulletGroup, bulletGroup, True, True) # check for bullets hit eachother
            
            self.check_if_bullets_got_hit(p_bulletGroup, bulletGroup)
            
            self.check_if_player_got_powerup(playerGroup, powerUpGroup, enemyGroup)
                        
            self.check_if_player_got_hit(playerGroup, bulletGroup, self.enemy_dmg)
            if len(playerGroup.sprites()) == 0:
                self.death_cb(self.score.score)
                continue
            
            
            
            hp.set_health(playerGroup.sprites()[0].hp) # type: ignore
            
            if len(enemyGroup) < enemyCounter:
                self.score.change_score(10)
                enemyCounter -= 1
                if random.random() > 0.8 and self.dg == None:
                    actor = random.choice(list(self.cheerups.keys()))
                    self.dg = GameDialogueWindow(
                        self.screen,
                        f"{actor}: {random.choice(self.cheerups[actor])}"
                    )

            if len(enemyGroup) <= 0 and len(waves) == 0:
                self.boss_level_cb(self.score)
                continue
            elif len(enemyGroup) <= 0 and len(waves) != 0 and self.dt % 35 == 0:
                self.cb = waves.pop(0)
                self.cb(enemyGroup, particleGroup, bulletGroup, powerUpGroup, nums_of_enemies.pop(0))
            elif len(enemyGroup) <= 0:
                self.dt += 1
                
            hp.update()
            stars.update()
            self.score.update()
            powerUpGroup.update(self.screen)
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

class Level2State(Level1State):
    def __init__(self, sc: Surface, score):
        super().__init__(sc)
        self.score = score
        self.enemy_dmg = 20
        self.boss_hp = 10000
    def win_cb(self,score):
        self.next_state = TransitionStateIn(self.screen, WinState(self.screen, score))
        self.should_change_state = True
    
    def run(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/themept2.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(10)
        
        clock = pygame.time.Clock()
        running = True

        powerUpGroup = Group()
        enemyGroup = Group()
        particleGroup = Group()
        bulletGroup = Group()
        p_bulletGroup = Group()
        playerGroup = Group()
        playerGroup.add(Spaceship(CFG.WIDTH // 2, CFG.HEIGHT - 50, pt=particleGroup, bt=p_bulletGroup))
        enemyGroup.add(Boss(50, 50, pt=particleGroup, bt=bulletGroup, pu=powerUpGroup, hp=10000))
        hp = Health(self.screen, playerGroup.sprites()[0].hp, playerGroup.sprites()[0].hp) # type: ignore
        boss_hp = BossHealth(self.screen, self.boss_hp, self.boss_hp)
        stars = Stars(self.screen)
        enemyCounter = 15
        
        while running:
            
            
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

            self.check_if_enemy_got_hit(enemyGroup, playerGroup)

            pygame.sprite.groupcollide(p_bulletGroup, bulletGroup, True, True) # check for bullets hit eachother
            
            self.check_if_bullets_got_hit(p_bulletGroup, bulletGroup)
            
            self.check_if_player_got_powerup(playerGroup, powerUpGroup, enemyGroup)
            self.check_if_player_got_hit(playerGroup, bulletGroup, self.enemy_dmg)
            
            if len(playerGroup.sprites()) == 0:
                self.death_cb(self.score.score)
                continue
            
            hp.set_health(playerGroup.sprites()[0].hp) # type: ignore
            
            
            if len(enemyGroup) < enemyCounter:
                self.score.change_score(10)
                enemyCounter -= 1
                if random.random() > 0.8 and self.dg == None:
                    actor = random.choice(list(self.cheerups.keys()))
                    self.dg = GameDialogueWindow(
                        self.screen,
                        f"{actor}: {random.choice(self.cheerups[actor])}"
                    )

            if len(enemyGroup) <= 0:
                self.win_cb(self.score.score)
                continue
            boss_hp.set_health(enemyGroup.sprites()[0].hp)
            
            hp.update()
            boss_hp.update()
            stars.update()
            self.score.update()
            powerUpGroup.update(self.screen)
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

class WinState(DeathState):
    
    def __init__(self, screen: Surface, score:int):
        super().__init__(screen, score)
        
        
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
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/sillythingy.wav")
        pygame.mixer.music.play()
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
        
        stars = Stars(self.screen)
        
        if self.new_highscore:
            score_message = self.my_font.render(f"!!You won and set your new highscore: {self.score}!!", True, THEME.WHITE)
        else:
            score_message = self.my_font.render(f"You won with score: {self.score}. Your highscore is: {self.prev_score}", True, THEME.WHITE)
        
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
            stars.update()
            
            if self.dg != None:
                self.dg.update()
                if self.dg.is_finished():
                    self.dg = None
            pygame.display.flip()
            self.clock.tick(75)

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
        self.next_state = TransitionStateIn(self.screen, FirstCutscene(self.screen))

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
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/mainmenu.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(10)
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
        stars = Stars(self.screen)
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
            stars.update()
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
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load("assets/sfx/tramst.wav")
        pygame.mixer.music.play()
        while not self.shouldStop:
            self.update()
        
        return self.next_state

    def update(self):
        self.df += 1
        if self.df % 3 == 0:
            
            self.image = pygame.transform.scale_by(self.image, 1.5)
            rect = self.image.get_rect(center=(self.screen.get_rect().center))

            if self.image.get_rect().h > CFG.HEIGHT and self.image.get_rect().w > CFG.WIDTH:
                self.shouldStop = True
            self.screen.blit(self.image, rect)
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
