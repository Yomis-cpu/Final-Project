import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600        
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Final Project")

clock = pygame.time.Clock()
FPS = 60

player_x = WIDTH // 2
player_y = HEIGHT // 2
player_size = 40                
player_speed = 5 


running = True

while running:
    dt = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:       
        player_y -= player_speed
    if keys[pygame.K_s]:       
        player_y += player_speed
    if keys[pygame.K_a]:        
        player_x -= player_speed
    if keys[pygame.K_d]:        
        player_x += player_speed

    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_size:
        player_x = WIDTH - player_size
    if player_y < 0:
        player_y = 0
    if player_y > HEIGHT - player_size:
        player_y = HEIGHT - player_size

    screen.fill((30, 30, 40))

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pygame.draw.rect(screen, (50, 200, 255), player_rect)

    # Update the screen
    pygame.display.flip()

pygame.quit()
