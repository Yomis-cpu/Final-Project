import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600        
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Final Project")

clock = pygame.time.Clock()
FPS = 60

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

        # Remove if outside screen
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



def main():
    player = Player()
    running = True

    while running:
        dt = clock.tick(FPS)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        # --- Update ---
        player.handle_movement(keys)
        player.shoot(mouse_pos, mouse_pressed)
        player.update_bullets()

        # --- Draw ---
        screen.fill((30, 30, 40))
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()