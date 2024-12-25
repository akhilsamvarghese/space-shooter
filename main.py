import pygame
import os
import time
import random
import math
from pathlib import Path

pygame.font.init()
pygame.display.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Create assets directory if it doesn't exist
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Default background color as fallback
DEFAULT_BG_COLOR = (0, 0, 20)  # Dark blue

# Helper function to safely load images
def load_image(path, fallback_color=None, size=None):
    try:
        if path.exists():
            img = pygame.image.load(str(path))
            if size:
                return pygame.transform.scale(img, size)
            return img
        else:
            if fallback_color:
                surf = pygame.Surface((50, 50) if not size else size)
                surf.fill(fallback_color)
                return surf
            raise FileNotFoundError(f"Image not found: {path}")
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        if fallback_color:
            surf = pygame.Surface((50, 50) if not size else size)
            surf.fill(fallback_color)
            return surf
        raise

# Load images with fallbacks
try:
    # Ships
    RED_SPACE_SHIP = load_image(assets_dir / "pixel_ship_red_small.png", (255, 0, 0))
    GREEN_SPACE_SHIP = load_image(assets_dir / "pixel_ship_green_small.png", (0, 255, 0))
    BLUE_SPACE_SHIP = load_image(assets_dir / "pixel_ship_blue_small.png", (0, 0, 255))
    YELLOW_SPACE_SHIP = load_image(assets_dir / "pixel_ship_yellow.png", (255, 255, 0))

    # Lasers
    RED_LASER = load_image(assets_dir / "pixel_laser_red.png", (255, 0, 0))
    GREEN_LASER = load_image(assets_dir / "pixel_laser_green.png", (0, 255, 0))
    BLUE_LASER = load_image(assets_dir / "pixel_laser_blue.png", (0, 0, 255))
    YELLOW_LASER = load_image(assets_dir / "pixel_laser_yellow.png", (255, 255, 0))

    # Background - create a starfield if image not found
    BG = load_image(assets_dir / "Space_Stars2.svg", None, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Error loading assets: {e}")
    # Create a simple starfield background
    BG = pygame.Surface((WIDTH, HEIGHT))
    BG.fill(DEFAULT_BG_COLOR)
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(1, 2)
        brightness = random.randint(128, 255)
        pygame.draw.circle(BG, (brightness, brightness, brightness), (x, y), radius)

# Load sound effects with fallback
try:
    LASER_SOUND = pygame.mixer.Sound(str(assets_dir / "Pew! Sound Effect [Pew Pew Pew]-[AudioTrimmer.com]-2.mp3"))
    LASER_SOUND.set_volume(0.5)  # Adjust volume to 50%
except Exception as e:
    print(f"Error loading laser sound: {e}")
    # Create an empty Sound object as fallback
    LASER_SOUND = pygame.mixer.Sound(buffer=bytes(24))  # Minimal valid sound

# New animation classes
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images = [pygame.Surface((50, 50)) for _ in range(5)]
        for i, img in enumerate(self.images):
            img.fill((255, 200 - i*40, 0))
            pygame.draw.circle(img, (255, 255, 200), (25, 25), 25 - i*5)
        self.index = 0
        self.counter = 0

    def draw(self, window):
        if self.counter % 5 == 0:
            self.index = (self.index + 1) % len(self.images)
        window.blit(self.images[self.index], (self.x, self.y))
        self.counter += 1

    def is_finished(self):
        return self.counter > 25

class StarField:
    def __init__(self, num_stars):
        self.stars = []
        for _ in range(num_stars):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.randint(1, 3)
            self.stars.append([x, y, speed])

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WIDTH)

    def draw(self, window):
        for star in self.stars:
            pygame.draw.circle(window, (255, 255, 255), (star[0], star[1]), 1)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        # Add trail effect
        for i in range(1, 5):
            alpha = 255 - i * 50
            trail_img = self.img.copy()
            trail_img.set_alpha(alpha)
            window.blit(trail_img, (self.x, self.y + i * 5))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
        
        # Add thrust animation
        if isinstance(self, Player):
            thrust_height = random.randint(10, 20)
            pygame.draw.polygon(window, (255, 100, 0), 
                                [(self.x + self.get_width()//2, self.y + self.get_height()),
                                 (self.x + self.get_width()//2 - 10, self.y + self.get_height() + thrust_height),
                                 (self.x + self.get_width()//2 + 10, self.y + self.get_height() + thrust_height)])

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            # Play sound effect when shooting
            LASER_SOUND.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 2

    player_vel = 8
    laser_vel = 8

    player = Player(300, 630, health=100) # Updated player health

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    star_field = StarField(100)
    explosions = []

    def redraw_window():
        WIN.blit(BG, (0,0))
        star_field.draw(WIN)
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        for explosion in explosions:
            explosion.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        star_field.update()
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player): # Updated enemy collision damage
                player.health -= 20
                explosions.append(Explosion(enemy.x, enemy.y))
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                explosions.append(Explosion(enemy.x, enemy.y))
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
        
        # Update and remove finished explosions
        explosions = [exp for exp in explosions if not exp.is_finished()]

def main_menu():
    title_font = pygame.font.SysFont("arial", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press to start...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

if __name__ == "__main__":
    main_menu()

