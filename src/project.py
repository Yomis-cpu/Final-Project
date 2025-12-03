import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600        
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Final Project")

clock = pygame.time.Clock()
FPS = 60

ENEMY_SPEED = 2.0
ENEMY_SIZE = 30
ENEMY_SPAWN_INTERVAL = 500

class Bullet:
    def __init__(self, x, y, dx, dy, speed=10, radius=5):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.radius = radius
        self.alive = True

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        
        if self.x < -10 or self.x > WIDTH + 10 or self.y < -10 or self.y > HEIGHT + 10:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 255, 0), (int(self.x), int(self.y)), self.radius)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 40
        self.speed = 5

        self.bullets = []  
        self.shoot_cooldown = 500   
        self.last_shot_time = 0

    def handle_movement(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

        
        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))

    def shoot(self, mouse_pos, mouse_pressed):
        if not mouse_pressed:
            return
        
        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.shoot_cooldown:
            return
        
        self.last_shot_time = now

        px = self.x + self.size / 2
        py = self.y + self.size / 2
        mx, my = mouse_pos

        dx = mx - px
        dy = my - py
        length = math.hypot(dx, dy)
        if length == 0:
            return

        dx /= length
        dy /= length

        new_bullet = Bullet(px, py, dx, dy)
        self.bullets.append(new_bullet)

    def update_bullets(self):
        for bullet in self.bullets:
            bullet.update()

        self.bullets = [b for b in self.bullets if b.alive]

    def draw(self, surf):
        pygame.draw.rect(surf, (50, 200, 255), (self.x, self.y, self.size, self.size))
        for b in self.bullets:
            b.draw(surf)

class Enemy:
    def __init__(self):
        self.size = ENEMY_SIZE
        self.speed = ENEMY_SPEED
        self.radius = self.size / 2

        
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.x = random.randint(0, WIDTH - self.size)
            self.y = -self.size
        elif side == "bottom":
            self.x = random.randint(0, WIDTH - self.size)
            self.y = HEIGHT + self.size
        elif side == "left":
            self.x = -self.size
            self.y = random.randint(0, HEIGHT - self.size)
        else:  # right
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT - self.size)

        self.alive = True

    def update(self, player):
        px = player.x + player.size / 2
        py = player.y + player.size / 2
        ex = self.x + self.size / 2
        ey = self.y + self.size / 2

        dx = px - ex
        dy = py - ey
        length = math.hypot(dx, dy)
        if length != 0:
            dx /= length
            dy /= length

        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, surf):
        pygame.draw.rect(surf, (200, 60, 60), (int(self.x), int(self.y), self.size, self.size))


def main():
    player = Player()
    enemies = []

    last_enemy_spawn = pygame.time.get_ticks()
    running = True

    while running:
        dt = clock.tick(FPS)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        
        player.handle_movement(keys)
        player.shoot(mouse_pos, mouse_pressed)
        player.update_bullets()

        now = pygame.time.get_ticks()
        if now - last_enemy_spawn > ENEMY_SPAWN_INTERVAL:
            enemies.append(Enemy())
            last_enemy_spawn = now

        for enemy in enemies:
            enemy.update(player)

        for enemy in enemies:
            if not enemy.alive:
                continue

            ex = enemy.x + enemy.size / 2
            ey = enemy.y + enemy.size / 2

            for bullet in player.bullets:
                if not bullet.alive:
                    continue
                
                bx = bullet.x
                by = bullet.y

                dist = math.hypot(ex - bx, ey - by)

                if dist < enemy.radius + bullet.radius:
                    enemy.alive = False
                    bullet.alive = False
                    break

        enemies = [e for e in enemies if e.alive]
        player.bullets = [b for b in player.bullets if b.alive]


        screen.fill((30, 30, 40))
        player.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()