import pygame
from pygame.sprite import Sprite, Group
from pygame.surface import Surface
from pygame.event import Event  # For syntax highlight
from pygame.key import ScancodeWrapper  # For syntax highlight
from pygame.image import load
from pygame.mixer import Sound


from config import CFG, THEME
from particles import Particle, SpaceshipParticle, DeathParticle, BulletParticle


from random import randint


class Bullet(Sprite):
    def __init__(self, x, y, pt):
        Sprite.__init__(self)
        self.image = Surface((16, 50))
        self.image.fill(THEME.RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = (
            y - 50
        )  # Made this because we are basically wanna spawn our bullets higher than player
        self.vel_y = 0
        self.vel_x = -10
        self.particles = pt

    def update(self, sc: Surface):
        if (
            self.rect.top < -200
        ):  # Also we dont wanna see how our bullets will disappear so we killing them only after they reach top -200 of whe world
            self.kill()
        self.rect.move_ip(self.vel_y, self.vel_x)

        sc.blit(self.image, self.rect)

        self.shit_particles()

    def shit_particles(self):
        pt = BulletParticle(self.rect.centerx - randint(-2, 2), self.rect.bottom, 25)
        self.particles.add(pt)

    def kill(self):
        super().kill()
        print("killed self")


class Spaceship(Sprite):
    piu_sound = Sound("assets/sfx/piu.wav")
    death_sound = Sound("assets/sfx/playerdeath.wav")
    piu_sound.set_volume(0.4)
    def __init__(self, x=100, y=100, pt: Group = Group()):
        Sprite.__init__(self)
        
        self.speed = 5
        self.image = load("assets/sprites/airkiller2.png")

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.particles = pt
        self.bullets = Group()
        self.bt = 0
        self.damage = 50
        
    def try_move_left(self):
        if self.rect.x - self.speed < 0:
            return
        self.rect.move_ip(-self.speed, 0)

    def try_move_right(self):
        if self.rect.right + self.speed > CFG.WIDTH:
            return
        self.rect.move_ip(self.speed, 0)

    def try_move_up(self):
        if self.rect.top - self.speed < 0:
            return
        self.rect.move_ip(0, -self.speed)

    def try_move_down(self):
        if self.rect.bottom + self.speed > CFG.HEIGHT:
            return
        self.rect.move_ip(0, self.speed)

    def update(self, sc: Surface):
        key = pygame.key.get_pressed()

        if key[pygame.K_DOWN]:
            self.shit_particles()

            self.try_move_down()

        if key[pygame.K_UP]:
            self.shit_particles()

            self.try_move_up()

        if key[pygame.K_LEFT]:
            self.shit_particles()

            self.try_move_left()

        if key[pygame.K_RIGHT]:
            self.shit_particles()

            self.try_move_right()

        if key[pygame.K_SPACE]:
            self.shoot()

        sc.blit(self.image, self.rect)

        self.bullets.update(sc)

    def shit_particles(self):
        particle = SpaceshipParticle(
            self.rect.centerx - randint(-4, 4), self.rect.bottom, 50
        )
        self.particles.add(particle)

    def shoot(self):
        self.bt += 1
        if self.bt % 10 != 0:
            return
        self.piu_sound.stop()
        self.piu_sound.play()
        bullet = Bullet(self.rect.centerx - 8, self.rect.topleft[1], self.particles)
        self.bullets.add(bullet)

    def kill(self):
        
        super().kill()
    

class Enemy(Spaceship):
    death_sound = Sound("assets/sfx/playerdeath.wav")
    hit_sound = Sound("assets/sfx/hits.wav")
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), hp:int = 100):
        super().__init__(x, y, pt)
        self.image = Surface((h, w))
        self.image.fill(THEME.WHITE)
        self.hp = hp
        
    def update(self, sc: Surface):
        #(x, y) = randint(0, 1), randint(0, 1)
        #if x == 0:
        #    self.try_move_down()
        #if x == 1:
        #    self.try_move_up()
        #if y == 0:
        #    self.try_move_left()
        #if y == 1:
        #   self.try_move_right()
        sc.blit(self.image, self.rect)

    def kill(self):
        for _ in range(10):
            pt = DeathParticle(self.rect.centerx, self.rect.centery, 300)
            self.particles.add(pt)
        self.death_sound.play()
        super().kill()
        print("Enemy was killed!")

    def reduce_hp(self, damage:int):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
        else:
            self.hit_sound.stop()
            self.hit_sound.play()