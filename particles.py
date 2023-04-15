from pygame.sprite import Sprite, Group
from pygame.surface import Surface
from random import randint

from config import CFG, THEME, FORMULAS


class Particle(Sprite):
    def __init__(self, x, y, lifetime):
        Sprite.__init__(self)

        self.image = Surface((5, 5))
        self.image.fill(THEME.YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = randint(-2, 2)
        self.vel_x = randint(-2, 2)
        self.lifetime = lifetime
        self.dt = 0

    
    def try_move_x(self):
        if self.rect.x + self.vel_x < 0 or self.rect.x + self.vel_x > CFG.WIDTH:
            self.vel_x = -self.vel_x
        self.rect.move_ip(self.vel_x, 0)

    def try_move_y(self):
        if self.rect.top + self.vel_y < 0 or self.rect.bottom + self.vel_y > CFG.HEIGHT:
            self.vel_y = -self.vel_y
        self.rect.move_ip(0, self.vel_y)

    
    def update(self, sc: Surface):
        self.try_move_x()
        self.try_move_y()
        
        self.image.set_alpha((self.lifetime - self.dt) ** 4 % 255)
        sc.blit(self.image, self.rect)
        self.dt += 1

        if self.dt > self.lifetime:
            self.die()

    def die(self):
        self.kill()


class BulletParticle(Particle):
    def __init__(self, x, y, lifetime):
        super().__init__(x, y, lifetime)
        self.image.fill(THEME.RED)
        self.vel_y = randint(0, 2)
        self.vel_x = randint(-1, 1)

def sign(number):
    if number > 0:
        return 1
    return -1

class DeathParticle(Particle):
    
    def __init__(self, x, y, lifetime):
        super().__init__(x, y, lifetime)
        self.image.fill(THEME.YELLOW)
        self.vel_y = randint(-10, 10)
        self.vel_x = randint(-10, 10)

    def update(self, sc: Surface):
        self.try_move_x()
        self.try_move_y()
        self.image.set_alpha((self.lifetime - self.dt) ** 4 % 255)
        sc.blit(self.image, self.rect)
        self.dt += 1
        
        if self.dt % 25 == 0:
            self.vel_x = max(abs(self.vel_x) - randint(0, 1), 0)  * sign(self.vel_x)
            self.vel_y = max(abs(self.vel_y) - randint(0, 1), 0)  * sign(self.vel_y)
        
        if self.vel_x == 0 or self.vel_y == 0:
            self.die()
        
        if self.dt > self.lifetime:
            self.die()

class SpaceshipParticle(Particle):
    def __init__(self, x, y, lifetime):
        super().__init__(x, y, lifetime)
        self.image.fill(THEME.GREEN)
        self.vel_y = randint(-2, 2)
        self.vel_x = randint(-2, 2)

    def update(self, sc: Surface):
        self.try_move_x()
        self.try_move_y()
        self.image.set_alpha((self.lifetime - self.dt) ** 4 % 255)
        sc.blit(self.image, self.rect)
        self.dt += 1

        if self.dt > self.lifetime:
            self.die()

class CursorParticle(Particle):
    def __init__(self, x, y, lifetime):
        super().__init__(x, y, lifetime)
        self.image.fill(tuple([randint(0, 255) for _ in range(3)]))

class StarParticle(Sprite):
    MAX_OPACITY = 255 // 2
    def __init__(self, x, y):
        Sprite.__init__(self)
        self.image = Surface((5, 5))
        self.image.fill(THEME.WHITE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.opacity = 1
        self.inc = True
        
        
    def update(self, screen: Surface):
        if self.inc:
            self.opacity += 1
        else:
            self.opacity -= 1
        
        if self.opacity >= self.MAX_OPACITY:
            self.inc = False
        
        if self.opacity == 0:
            self.kill()
        
        self.image.set_alpha(self.opacity)
        
        screen.blit(self.image, self.image.get_rect(center=(self.x, self.y)))