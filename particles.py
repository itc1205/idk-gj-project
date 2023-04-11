from pygame.sprite import Sprite, Group
from pygame.surface import Surface
from random import randint

from config import THEME, FORMULAS


class Particle(Sprite):
    def __init__(self, x, y, lifetime):
        Sprite.__init__(self)

        self.image = Surface((5, 5))
        self.image.fill(THEME.YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = randint(1, 3)
        self.vel_x = randint(-2, 2)
        self.lifetime = lifetime
        self.dt = 0

    def update(self, sc: Surface):
        self.rect.move_ip(self.vel_x, self.vel_y)
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
        self.vel_y = randint(1, 2)
        self.vel_x = randint(-1, 1)


class DeathParticle(Particle):
    def __init__(self, x, y, lifetime):
        super().__init__(x, y, lifetime)
        self.image.fill(THEME.YELLOW)
        self.vel_y = randint(-2, 2)
        self.vel_x = randint(-2, 2)

    def update(self, sc: Surface):
        self.rect.move_ip(self.vel_x, self.vel_y)
        self.image.set_alpha(FORMULAS.P_DEATH(self.lifetime, self.dt))
        sc.blit(self.image, self.rect)
        self.dt += 1

        if self.dt > self.lifetime:
            self.die()


class SpaceshipParticle(Particle):
    def __init__(self, x, y, lifetime):
        super().__init__(x, y, lifetime)
        self.image.fill(THEME.GREEN)
        self.vel_y = randint(-2, 2)
        self.vel_x = randint(-2, 2)

    def update(self, sc: Surface):
        self.rect.move_ip(self.vel_x, self.vel_y)
        self.image.set_alpha((self.lifetime - self.dt) ** 4 % 255)
        sc.blit(self.image, self.rect)
        self.dt += 1

        if self.dt > self.lifetime:
            self.die()
