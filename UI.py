from copy import copy
import pygame

from config import THEME, CFG

from pygame import Rect
from pygame.surface import Surface
from random import choice


class BUTTON_STATE:
    NORMAL = 0
    HOVER = 1
    CLICKED = 2

class Button():
    sound_hover = pygame.mixer.Sound("assets/sfx/butonhover.wav")
    sound_press = pygame.mixer.Sound("assets/sfx/butonpres.wav")
    sound_hover.set_volume(0.4)
    sound_press.set_volume(0.4)
    
    def __init__(self, x:int, y: int, w:int, h: int, screen: Surface) -> None:
        self.rect = Rect(x, y, w, h)
        
        self.image_base = Surface((w, h))
        self.image_base.fill(THEME.WHITE)
        
        self.image_hover = Surface((w, h))
        self.image_hover.fill(THEME.YELLOW)
        
        self.image_press = Surface((w, h))
        self.image_press.fill(THEME.GREEN)
        
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
            

class DialogueWindow():
    unaudible_chars = set(",.!\"\' ")
    my_font = pygame.font.SysFont('Comic Sans MS', 30)
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
        
        
    def update(self):
        self.lt += 1
        
        if (self.lt % 8 == 0) and (self.cur_index < len(self.text) and self.cur_index + 1 < self.MAX_CHARS):
            self.lines[-1] += self.text[self.cur_index]
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

        
        