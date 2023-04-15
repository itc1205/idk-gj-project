import pygame
from pygame.sprite import Sprite, Group
from pygame.surface import Surface
from pygame.event import Event  # For syntax highlight
from pygame.key import ScancodeWrapper  # For syntax highlight
from pygame.image import load
from pygame.mixer import Sound


from config import CFG, THEME
from particles import SpaceshipParticle, DeathParticle, BulletParticle


from random import randint


class Bullet(Sprite):
    def __init__(self, x, y, pt, vel_x, vel_y, color: tuple[int, int, int]):
        Sprite.__init__(self)
        self.image = Surface((8, 25))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = (
            y - 25
        ) # Made this because we are basically wanna spawn our bullets higher than player
        self.vel_y = vel_y
        self.vel_x = vel_x
        self.particles = pt

    def update(self, sc: Surface):
        if (
            self.rect.top < -200 or
            self.rect.bottom > CFG.HEIGHT
        ):  # Also we dont wanna see how our bullets will disappear so we killing them only after they reach top -200 of whe world
            self.kill()
        self.rect.move_ip(self.vel_y, self.vel_x)

        sc.blit(self.image, self.rect)

        self.shit_particles()

    def shit_particles(self):
        pt = BulletParticle(self.rect.centerx - randint(-2, 2), self.rect.bottom, 25)
        self.particles.add(pt)

    def kill(self):
        for _ in range(3):
            pt = BulletParticle(self.rect.centerx, self.rect.centery, 50)
            self.particles.add(pt)
        super().kill()


class Spaceship(Sprite):
    piu_sound = Sound("assets/sfx/piu.wav")
    death_sound = Sound("assets/sfx/playerdeath.wav")
    piu_sound.set_volume(0.4)
    image = load("assets/sprites/hero.png")
    hit_sound = Sound("assets/sfx/hits.wav")
    def __init__(self, x=100, y=100, pt: Group = Group(), bt: Group = Group()):
        Sprite.__init__(self)
        
        self.speed = 4
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.particles = pt
        self.bullets = bt
        self.bt = 0
        self.damage = 50
        self.b_vel_x, self.b_vel_y = -10, 0
        self.lt = 0
        self.hp = 200
        
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
        self.lt += 1
        next_speed = 0
        
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

        if key[pygame.K_LSHIFT]:
            next_speed += 1

        
        if next_speed == 0:
            self.speed = 6
        else:
            if self.lt % 50 == 0:
                self.speed = min(self.speed + 1, 10)
        
        
        sc.blit(self.image, self.rect)

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
        bullet = Bullet(self.rect.centerx - 4, self.rect.topleft[1], self.particles, self.b_vel_x, self.b_vel_y, THEME.GREEN)
        self.bullets.add(bullet)

    def reduce_hp(self, damage:int):
        self.hp -= damage
        
        if self.hp <= 0:
            self.kill()
        else:
            self.hit_sound.stop()
            self.hit_sound.play()
    
    def kill(self):
        
        super().kill()
    

class Enemy(Spaceship):
    image = load("assets/sprites/enemy.png")
    death_sound = Sound("assets/sfx/playerdeath.wav")
    hit_sound = Sound("assets/sfx/hits.wav")
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(), hp:int = 100):
        super().__init__(x, y, pt, bt)
        #self.image = Surface((h, w))
        #self.image.fill(THEME.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = hp
        self.vel_y = 0
        self.vel_x = 0
        self.lt = 0
        self.b_vel_x, self.b_vel_y = 10, 0
        
    def try_move_x(self):
        if self.rect.x + self.vel_x < 0 or self.rect.x + self.vel_x > CFG.WIDTH:
            self.vel_x = -self.vel_x
        self.rect.move_ip(self.vel_x, 0)

    def try_move_y(self):
        if self.rect.top + self.vel_y < 0 or self.rect.bottom + self.vel_y > CFG.HEIGHT:
            self.vel_y = -self.vel_y
        self.rect.move_ip(0, self.vel_y)
    
    def update(self, sc: Surface):        
        self.lt += 1
        
        if self.lt % 25 == 0:
            self.vel_x = randint(-2, 2)
            self.shoot()
        self.try_move_y()
        self.try_move_x()
        sc.blit(self.image, self.rect)

    def shoot(self):
        self.bt += 1
        if randint(0, 1):
            return
        self.piu_sound.stop()
        self.piu_sound.play()
        bullet = Bullet(self.rect.centerx - 4, self.rect.bottomleft[1], self.particles, self.b_vel_x, self.b_vel_y, THEME.RED)
        self.bullets.add(bullet)
    
    def kill(self):
        for _ in range(15):
            pt = DeathParticle(self.rect.centerx, self.rect.centery, 300)
            self.particles.add(pt)
        self.death_sound.play()
        super().kill()

    def reduce_hp(self, damage:int):
        self.hp -= damage
        
        if self.hp <= 0:
            self.kill()
        else:
            self.hit_sound.stop()
            self.hit_sound.play()

class Boss(Enemy):
    image = Surface((200, 200))#load("assets/sprites/boss.png")
    image.fill((128, 128, 128))
    death_sound = Sound("assets/sfx/playerdeath.wav")
    hit_sound = Sound("assets/sfx/hits.wav")
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(), hp: int = 1000):
        super().__init__(x, y, h, w, pt, bt, hp)