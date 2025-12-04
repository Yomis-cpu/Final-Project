import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600        
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Final Project")

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 64)

ENEMY_SPEED = 2.0
ENEMY_SIZE = 30
ENEMY_SPAWN_INTERVAL = 500

PLAYER_MAX_HEALTH = 100
PLAYER_DAMAGE = 10
PLAYER_HIT_COOLDOWN = 500

EXP_PER_ENEMY = 10
BASE_EXP_TO_NEXT = 100

class HealthBar:
    def __init__(self, x, y, width, height, max_value, color=(0, 255, 0), bg_color=(80, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_value = max_value
        self.current_value = max_value

        self.color = color
        self.bg_color = bg_color

    def update(self, new_value):
        self.current_value = max(0, min(new_value, self.max_value))

    def draw(self, surf):
        pygame.draw.rect(surf, self.bg_color, (self.x, self.y, self.width, self.height))

        ratio = self.current_value / self.max_value
        pygame.draw.rect(surf, self.color, (self.x, self.y, int(self.width * ratio), self.height))

class ExpOrb:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.radius = 6
        self.amount = amount
        self.alive = True

    def update(self, player):
        px = player.x + player.size / 2
        py = player.y + player.size / 2
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)

        if dist < 150 and dist != 0:
            dx /= dist
            dy /= dist
            self.x += dx * 7
            self.y += dy * 7

    def draw(self, surf):
        pygame.draw.circle(surf, (100, 255, 100), (int(self.x), int(self.y)), self.radius) 


class ExpBar:
    def __init__(self, x, y, width, height, color=(50, 120, 255), bg_color=(40, 40, 40)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.bg_color = bg_color

        self.current = 0
        self.max = 1

    def update(self, current_value, max_value):
        self.current = current_value
        self.max = max_value

    def draw(self, surf):
        
        pygame.draw.rect(surf, self.bg_color, (self.x, self.y, self.width, self.height))

        ratio = self.current / self.max if self.max > 0 else 0

        pygame.draw.rect(
            surf,
            self.color,
            (self.x, self.y, int(self.width * ratio), self.height)
        )


class Bullet:
    def __init__(self, x, y, dx, dy, speed=10, radius=5, pierce=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.radius = radius
        self.pierce = pierce
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

        self.spread_level = 0
        self.pierce_level = 0

        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.last_hit_time = 0
        self.hit_cooldown = PLAYER_HIT_COOLDOWN

        self.health_bar = HealthBar(10, 10, 200, 20, self.max_health)

        self.level = 1
        self.exp = 0
        self.exp_to_next = BASE_EXP_TO_NEXT 
        self.exp_bar = ExpBar(10, 40, 200, 10)
        self.exp_bar.update(self.exp, self.exp_to_next)


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
        base_angle = math.atan2(dy, dx)

        new_bullet = Bullet(px, py, dx, dy)
        self.bullets.append(new_bullet)

        if self.spread_level == 0:
            num_bullets = 1
            total_spread = 0
        elif self.spread_level == 1:
            num_bullets = 4
            total_spread = math.radians(25)
        else:
            num_bullets = 8
            total_spread = math.radians(40)

        if self.pierce_level == 0:
            pierce_hits = 0
        elif self.pierce_level == 1:
            pierce_hits = 1
        elif self.pierce_level == 2:
            pierce_hits = 2
        elif self.pierce_level == 3:
            pierce_hits = 3
        else:
            pierce_hits = 999
        
        for i in range(num_bullets):
            if num_bullets == 1:
                angle_offset = 0
            else:
                t = i / (num_bullets - 1)  # 0..1
                angle_offset = -total_spread / 2 + total_spread * t
            angle = base_angle + angle_offset
            bdx = math.cos(angle)
            bdy = math.sin(angle)
            self.bullets.append(Bullet(px, py, bdx, bdy, pierce=pierce_hits))


    def update_bullets(self):
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.alive]

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.last_hit_time < self.hit_cooldown:
            return
        
        self.last_hit_time = now
        self.health -= amount
        if self.health < 0:
            self.health = 0
        
        self.health_bar.update(self.health  )

    def gain_exp(self, amount):
        self.exp += amount
        levels_gained = 0

        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            levels_gained += 1

            self.exp_to_next = int(self.exp_to_next * 1.5)

            self.health = self.max_health
            self.health_bar.update(self.health)
        
        self.exp_bar.update(self.exp, self.exp_to_next)

        return levels_gained
    
    def apply_upgrade_shoot_faster(self):
        self.shoot_cooldown = max(150, int(self.shoot_cooldown * 0.7))

    def apply_upgrade_spread(self):
        self.spread_level = min(self.spread_level + 1, 3)

    def apply_upgrade_pierce(self):
        self.pierce_level = min(self.pierce_level + 1, 3)

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
    exp_orbs = []

    last_enemy_spawn = pygame.time.get_ticks()
    running = True
    game_over = False
    choosing_upgrade = False
    pending_upgrades = 0

    while running:
        dt = clock.tick(FPS)

        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

        upgrade_btn_w = 260
        upgrade_btn_h = 60
        upgrade_x = WIDTH // 2 - upgrade_btn_w // 2
        upgrade_y_start = HEIGHT // 2 - 110
        upgrade_rects = [pygame.Rect(upgrade_x, upgrade_y_start + i * 80, upgrade_btn_w, upgrade_btn_h) for i in range(3)]

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(mouse_pos):
                    player = Player()
                    enemies = []
                    last_enemy_spawn = pygame.time.get_ticks()
                    game_over = False
                    pending_upgrades = 0
                    choosing_upgrade = False

            if choosing_upgrade and event.type == pygame.MOUSEBUTTONDOWN:
                if upgrade_rects[0].collidepoint(mouse_pos):
                    player.apply_upgrade_shoot_faster()
                    pending_upgrades -= 1
                elif upgrade_rects[1].collidepoint(mouse_pos):
                    player.apply_upgrade_spread()
                    pending_upgrades -= 1
                elif upgrade_rects[2].collidepoint(mouse_pos):
                    player.apply_upgrade_pierce()
                    pending_upgrades -= 1

                if pending_upgrades <= 0:
                    choosing_upgrade = False
        
        if game_over:
            screen.fill((10, 0, 0))

            game_over_text = big_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
            
            restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
            pygame.draw.rect(screen, (200, 200, 200), restart_button_rect, border_radius=10)

            restart_text = font.render("Restart", True, (0, 0, 0))
            screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2, restart_button_rect.centery - restart_text.get_height() // 2,))

            pygame.display.flip()
            continue

        if choosing_upgrade:
            screen.fill((20, 20, 30))

            title = big_font.render("LEVEL UP!", True, (255, 255, 0))
            screen.blit(
                title,
                (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 200)
            )

            options = [
                "Shoot Faster",
                "Spread Shot",
                "Piercing Bullets"
            ]

            for rect, text in zip(upgrade_rects, options):
                pygame.draw.rect(screen, (230, 230, 230), rect, border_radius=10)
                label = font.render(text, True, (0, 0, 0))
                screen.blit(
                    label,
                    (rect.centerx - label.get_width() // 2,
                     rect.centery - label.get_height() // 2)
                )

            pygame.display.flip()
            continue
            
        keys = pygame.key.get_pressed()
  
        player.handle_movement(keys)
        player.shoot(mouse_pos, mouse_pressed)
        player.update_bullets()

        now = pygame.time.get_ticks()
        if now - last_enemy_spawn > ENEMY_SPAWN_INTERVAL:
            enemies.append(Enemy())
            last_enemy_spawn = now

        for enemy in enemies:
            enemy.update(player)

        for orb in exp_orbs:
            orb.update(player)

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
                    exp_orbs.append(ExpOrb(ex, ey, EXP_PER_ENEMY))
                    break


        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        for enemy in enemies:
            enemy_rect = pygame.Rect(int(enemy.x), int(enemy.y), enemy.size, enemy.size)
            if enemy_rect.colliderect(player_rect):
                player.take_damage(PLAYER_DAMAGE)

        px_center = player.x + player.size / 2
        py_center = player.y + player.size / 2
        for orb in exp_orbs:
            if not orb.alive:
                continue
            dist = math.hypot(orb.x - px_center, orb.y - py_center)
            if dist < orb.radius + player.size / 2:
                orb.alive = False
                gained = player.gain_exp(orb.amount)
                if gained > 0:
                    pending_upgrades += gained
                    choosing_upgrade = True


        enemies = [e for e in enemies if e.alive]
        player.bullets = [b for b in player.bullets if b.alive]
        exp_orbs = [o for o in exp_orbs if o.alive]

        
        if player.health <= 0:
            game_over = True
            continue
            
        screen.fill((30, 30, 40))
        player.draw(screen)

        for orb in exp_orbs:
            orb.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        player.health_bar.draw(screen)
        player.exp_bar.draw(screen)

        lvl_text = font.render(f"LV: {player.level}", True, (255, 255, 255))
        screen.blit(lvl_text, (10, 55))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()