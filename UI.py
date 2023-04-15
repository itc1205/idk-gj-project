from copy import copy
import pygame

from config import THEME, CFG

from pygame import Rect
from pygame.surface import Surface
from random import choice, randint
from particles import DeathParticle, Particle, StarParticle



class BUTTON_STATE:
    NORMAL = 0
    HOVER = 1
    CLICKED = 2

class Button():
    sound_hover = pygame.mixer.Sound("assets/sfx/butonhover.wav")
    sound_press = pygame.mixer.Sound("assets/sfx/butonpres.wav")
    sound_hover.set_volume(0.4)
    sound_press.set_volume(0.4)
    
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 30)

    
    def __init__(self, x:int, y: int, w:int, h: int, screen: Surface, text:str, callback) -> None:
        self.rect = Rect(x, y, w, h)
        
        self.image_base = pygame.image.load("assets/sprites/button-base.png")
        #self.image_base.fill(THEME.WHITE)
        
        self.render_text = self.my_font.render(text, True, THEME.BLACK)
        
        self.image_hover = pygame.image.load("assets/sprites/button-hov.png")
        #self.image_hover.fill(THEME.YELLOW)
        
        self.image_press = Surface((w, h))
        self.image_press.fill(THEME.GREEN)
        self.cb = callback
        self.screen = screen
        self.button_state = BUTTON_STATE.NORMAL
        
        
    def update(self):
        (x, y) = pygame.mouse.get_pos()
        
        if self.button_state == BUTTON_STATE.NORMAL:
            if self.rect.collidepoint(x, y):
                self.sound_hover.stop()
                self.sound_hover.play()
                self.button_state = BUTTON_STATE.HOVER
        
        if self.button_state == BUTTON_STATE.HOVER:
            if not self.rect.collidepoint(x, y):
                self.button_state = BUTTON_STATE.NORMAL
   
            elif pygame.mouse.get_pressed()[0]:
                self.sound_hover.stop()
                self.sound_press.stop()
                self.sound_press.play()
                self.button_state = BUTTON_STATE.CLICKED
            

        if self.button_state == BUTTON_STATE.CLICKED:
            if not pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    self.button_state = BUTTON_STATE.HOVER
                else:
                    self.button_state = BUTTON_STATE.NORMAL
        
        
        
        if self.button_state == BUTTON_STATE.NORMAL:
            self.screen.blit(self.image_base, self.rect)
        elif self.button_state == BUTTON_STATE.HOVER:
            self.screen.blit(self.image_hover, self.rect)
        else:
            self.screen.blit(self.image_press, self.rect)
            self.cb()
        rect = self.render_text.get_rect()
        rect.center = self.rect.center
        self.screen.blit(self.render_text, rect)
        
class DialogueWindow():
    unaudible_chars = set(",.!\"\' ")
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 30)
    sounds = [
        pygame.mixer.Sound(sound) for sound in [
            f"assets/sfx/120bpmsamle{i}.wav" for i in range(1, 5)
            ] 
    ] # The funniest code i've ever wrote
    
    
    def __init__(self, screen: Surface, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi vitae nibh purus. Sed in risus eu augue sagittis porta.") -> None:
        self.MAX_CHARS = 118
        self.padding = 10
        self.background = Surface((CFG.WIDTH, 200))
        self.background.fill(THEME.RED)
        self.rect = Rect(0, CFG.HEIGHT - 200, CFG.WIDTH, 200)
        self.text_rect = Rect(self.padding, CFG.HEIGHT - 200 + self.padding, CFG.WIDTH, 200)
        self.screen = screen
        self.text = text
        self.rendered_lines = []
        self.lines = [""]
        self.current_text = ""
        self.lt = 0
        self.cur_index = 0
        self.font_h = self.my_font.size("A")[-1]
        self._finished = False
        self.life_after = 45
    
    def is_finished(self):
        return self._finished and self.life_after <= 0
    
    def update(self):
        self.lt += 1
        
        if not self._finished:
            self._finished = not bool(self.cur_index + 1 - len(self.text))
        
        if self._finished:
            self.life_after -= 1
        
        if (self.lt % 5 == 0) and (self.cur_index < len(self.text) and self.cur_index + 1 < self.MAX_CHARS):
            self.lines[-1] += self.text[self.cur_index] #Appending last line
            
            if self.text[self.cur_index] not in self.unaudible_chars:
                choice(self.sounds).play()
            self.cur_index += 1

            
        if (self.my_font.size(self.lines[-1])[0] > CFG.WIDTH - 20):
            self.lines.append(self.lines[-1].split().pop())
            
            self.lines[-2] = " ".join(self.lines[-2].split()[:-1])
            
        
        self.screen.blit(self.background, self.rect)
        for i in range(len(self.lines)):
            rect = copy(self.text_rect)
            rect.y += ( self.font_h) * i
            render_text = self.my_font.render(self.lines[i], True, THEME.BLACK)
            self.screen.blit(render_text, copy(rect))


class GameDialogueWindow(DialogueWindow):
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 20)
    
    def __init__(self, screen: Surface, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi vitae nibh purus. Sed in risus eu augue sagittis porta.") -> None:
        super().__init__(screen, text)
        self.background = Surface((CFG.WIDTH, 50))
        self.background.fill(THEME.RED)
        self.rect = Rect(0, CFG.HEIGHT - 50, CFG.WIDTH, 50)
        self.text_rect = Rect(self.padding, CFG.HEIGHT - 50 + self.padding, CFG.WIDTH, 50)
        self.MAX_CHARS = 50
    
    
    
    
class Score():
    my_font = pygame.font.Font("assets/font/Minecraft.ttf", 30)
    
    def __init__(self, sc:Surface) -> None:
        self.score = 0
        self.screen = sc
    def update(self):
        surface = self.my_font.render(f"Score: {self.score}", True, THEME.WHITE)
        rect = surface.get_rect()
        rect.center = (CFG.WIDTH // 2, 20)
        self.screen.blit(surface, rect)
        
    def change_score(self, score_change: int):
        self.score += score_change
    
class Stars():
    def __init__(self, sc:Surface) -> None:
        self.particle_g = pygame.sprite.Group()
        self.screen = sc
        self.dt = 0
    
    def update(self):
        self.dt += 1
        
        if self.dt % 75 == 0:
            for _ in range(5):
                x, y = randint(0, CFG.WIDTH), randint(0, CFG.HEIGHT)
                self.particle_g.add(StarParticle(x, y))
        
        self.particle_g.update(self.screen)