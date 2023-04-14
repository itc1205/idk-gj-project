from init import init_window
from states import STATES
import pygame

class Game:
    def __init__(self):
        self.screen = init_window()
        self.state = STATES.MAIN_MENU(self.screen)
        
    def run(self):
        
        while True:
            self.change_state(self.state.run())

    def change_state(self, state):
        self.state = state
