import pygame
from pygame.sprite import Sprite, Group
from pygame.surface import Surface
from pygame.event import Event  # For syntax highlight
from pygame.key import ScancodeWrapper  # For syntax highlight
from pygame.image import load
from pygame.mixer import Sound


from config import CFG, THEME
from particles import SpaceshipParticle, DeathParticle, BulletParticle


from random import randint, random, choice


class Bullet(Sprite):
    def __init__(self, x, y, pt, vel_x, vel_y, color: tuple[int, int, int], damage=20):
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
        self.damage = damage
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
    def die(self):
        self.kill()

class EnemyBullet(Bullet):
    def shit_particles(self):
        pt = BulletParticle(self.rect.centerx - randint(-2, 2), self.rect.top, 25)
        self.particles.add(pt)

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
        bullet = EnemyBullet(self.rect.centerx - 4, self.rect.topleft[1], self.particles, self.b_vel_x, self.b_vel_y, THEME.GREEN)
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
    
    def die(self):
        self.kill()
    
class Enemy(Spaceship):
    image = load("assets/sprites/enemy.png")
    death_sound = Sound("assets/sfx/playerdeath.wav")
    hit_sound = Sound("assets/sfx/hits.wav")
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(),pu: Group = Group(), hp:int = 100, dmg:int = 20):
        super().__init__(x, y, pt, bt)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = hp
        self.vel_y = 0
        self.vel_x = 0
        self.lt = 0
        self.b_vel_x, self.b_vel_y = 10, 0
        self.pu = pu
        self.max_y_vel = 0
        self.max_x_vel = 2
        self.drop_type = [PowerUPs.HEAL,] #PowerUPs.POINTS]#[PowerUPs.KILL_ALL]
        self.drop_factor = 1 #0.6 
        self.dmg = dmg
        self.change_factor = 25
        self.bullet_color = THEME.BLUE
    
    def try_move_x(self):
        if self.rect.left + self.vel_x < 0 or self.rect.right + self.vel_x > CFG.WIDTH:
            self.vel_x = -self.vel_x
        self.rect.move_ip(self.vel_x, 0)

    def try_move_y(self):
        if self.rect.top + self.vel_y < 0 or self.rect.bottom + self.vel_y > CFG.HEIGHT - 200:
            self.vel_y = -self.vel_y
        self.rect.move_ip(0, self.vel_y)
    
    def update(self, sc: Surface):        
        self.lt += 1
        
        if self.lt % self.change_factor == 0:
            self.vel_x = randint(-self.max_x_vel, self.max_x_vel)
            self.vel_y = randint(-self.max_y_vel, self.max_y_vel)
            self.shoot()
        self.try_move_y()
        self.try_move_x()
        sc.blit(self.image, self.rect)

    def shoot(self):
        self.bt += 1
        if random() < 0.7:
            return
        self.piu_sound.stop()
        self.piu_sound.play()
        bullet = Bullet(self.rect.centerx - 4, self.rect.bottom, self.particles, self.b_vel_x, self.b_vel_y, self.bullet_color, damage=self.dmg)
        self.bullets.add(bullet)
    
    def kill(self):
        if random() < self.drop_factor:
            powerup = PowerUP(self.rect.x, self.rect.y)
            powerup.change_type(choice(self.drop_type))
            self.pu.add(powerup)
            
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

class FastEnemy(Enemy):
    image = pygame.transform.scale_by(load("assets/sprites/enemy4.png"), 2)
    
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(), pu: Group = Group(), hp: int = 100):
        super().__init__(x, y, h, w, pt, bt, pu, hp)
        self.hp = 20
        self.max_x_vel = 10
        self.max_y_vel = 10
        self.damage = 15
        self.bullet_color = THEME.YELLOW
        self.change_factor = 15
        self.drop_factor = 0.1
        self.drop_type = [PowerUPs.KILL_ALL, PowerUPs.HEAL]
        
class SlowEnemy(Enemy):
    image = pygame.transform.scale_by(load("assets/sprites/enemy3.png"), 2)
    
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(), pu: Group = Group(), hp: int = 100):
        super().__init__(x, y, h, w, pt, bt, pu, hp)
        self.hp = 200
        self.max_x_vel = 1
        self.max_y_vel = 1
        self.damage = 50
        self.change_factor = 144
        self.bullet_color = THEME.RED
        self.drop_factor = 1
        self.drop_type = [ PowerUPs.POINTS]
class ShitEnemy(Enemy):
    image = pygame.transform.scale_by(load("assets/sprites/enemy2.png"), 2)
    
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(), pu: Group = Group(), hp: int = 100):
        super().__init__(x, y, h, w, pt, bt, pu, hp)
        self.hp = 150
        self.max_x_vel = 5
        self.max_y_vel = 5
        self.damage = 25
        self.bullet_color = THEME.BLUE
        self.change_factor = 25
        self.drop_factor = 0.25
        self.drop_type = [ PowerUPs.HEAL ]
        
class Boss(Enemy):
    
    image = pygame.transform.scale_by(load("assets/sprites/boss.png"), 2)
    death_sound = Sound("assets/sfx/playerdeath.wav")
    hit_sound = Sound("assets/sfx/hits.wav")
    def __init__(self, x=10, y=10, h=20, w=20, pt: Group = Group(), bt: Group = Group(), pu: Group = Group(), hp: int = 1000):
        super().__init__(x, y, h, w, pt=pt, bt=bt, hp=hp, pu=pu)
        self.damage = 50
        self.max_x_vel = 10
        self.max_y_vel = 1
        self.change_factor = 25
    
    def shoot(self):
        self.bt += 1
        
        if self.bt % 144 == 0:
            powerup = PowerUP(self.rect.x, self.rect.y)
            powerup.change_type(PowerUPs.HEAL)
            self.pu.add(powerup)
        if random() < 0.5:
            return
        
        self.piu_sound.stop()
        self.piu_sound.play()
        for _ in range(10):
            self.b_vel_x = randint(5, 25)
            bullet =  Bullet(self.rect.centerx - 4, self.rect.bottom, self.particles, self.b_vel_x, self.b_vel_y, self.bullet_color, damage=self.dmg)
            self.bullets.add(bullet)        

class PowerUPs():
    HEAL = 0
    POINTS = 1
    KILL_ALL = 2


class PowerUP(Sprite):
    exp_image = pygame.image.load("assets/sprites/exp.png")
    nuke_image = pygame.image.load("assets/sprites/nuke.png")
    heal_image = pygame.image.load("assets/sprites/heal.png")
    
    pUp_sound = pygame.mixer.Sound("assets/sfx/pspawn.wav")
    
    def __init__(self, x, y) -> None:
        super().__init__()
        self.type = 0
        self.image = pygame.Surface((10, 10))
        self.image.fill(THEME.WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 5
        
    def change_type(self, type:int):
        self.type = type
        if self.type == PowerUPs.HEAL:
            self.image = self.heal_image
        elif self.type == PowerUPs.KILL_ALL:
                self.image = self.nuke_image
        elif self.type == PowerUPs.POINTS:
                self.image = self.exp_image

        self.rect = self.image.get_rect(center=self.rect.center)
    def check_bounds(self):
        if (
            self.rect.top < -200 or
            self.rect.bottom > CFG.HEIGHT
        ):  # Also we dont wanna see how our bullets will disappear so we killing them only after they reach top -200 of whe world
            self.kill()
       
    def update(self, screen: Surface):
        self.rect.move_ip(0, self.vel_y)
        self.check_bounds()
        screen.blit(self.image, self.rect)
    
     
    def die(self):
        self.pUp_sound.stop()
        self.pUp_sound.play()
        self.kill()