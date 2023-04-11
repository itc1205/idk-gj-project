from init import init_window
from states import STATES



class Game:
    def __init__(self):
        self.screen = init_window()
        self.state = STATES.LEVEL_1(self.screen)
    def run(self):
        
        while True:
            self.change_state(self.state.run())
            print("State has been changed")

    def change_state(self, state):
        
        self.state = state
