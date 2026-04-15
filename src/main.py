import pygame
import os
import sys
import random

# Asset Path Configuration 
GAME_PATH = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(filename: str) -> str:
    '''Returns the path to an asset file, given its filename.'''
    return os.path.join(GAME_PATH, "assets", filename)

#Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 640, 480
FPS = 60
BG_COLOR = (0, 0, 0)
GHOST_COLOR = (0, 255, 255)
PACMAN_COLOR = (255, 255, 0)
TILE_SIZE = 32

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Hunt: The Ghosts Strike Back")


# Maze Layout: each character is one TILE
# w = wall, . = pellet, ' ' = empty space, G = ghost start, P = pacman start
# 20 columns wide, 15 rows tall (640x480 with TILE_SIZE = 32)
MAZE_LAYOUT = [
    "WWWWWWWWWWWWWWWWWWWW",  # 20 W's (top border)

    "W........W.P.......W",
    "W.WWWW.W.WWWW.W...WW",
    "W.W....W....W.W...WW",
    "W.W.WWWWWW.WW.W...WW",
    "W................WWW",
    "W.W.WW.WWW.WW.W...WW",
    "W.W..G.........G..WW",
    "W.WWWW.W.WWWW.W...WW",
    "W.......W........WWW",
    "W.WWWW.W.WWWW.W...WW",
    "W.W....W....W.W...WW",
    "W.W.WWWWWW.WW.W...WW",
    "W................WWW",

    "WWWWWWWWWWWWWWWWWWWW",  # 20 W's (bottom border)
]

def build_level_from_layout(layout):
    walls = []
    pellets = []
    ghost_starts = []
    pacman_start = None
    
    rows = len(layout)
    cols = len(layout[0])
    
    for row in range(rows):
        for col in range(cols):
            ch = layout[row][col]
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            
            if ch == 'W':
                walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            elif ch == '.':
                pellets.append(pygame.Rect(x + TILE_SIZE // 4, y + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE //2 ))
            elif ch == 'G':
                ghost_starts.append((x, y))
            elif ch == "P":
                pacman_start = (x, y)
    
    return walls, pellets, ghost_starts, pacman_start
        
class Level:
    def __init__(self, layout):
        (self.walls, self.pellets, self.ghost_starts, self.pacman_start) = build_level_from_layout(layout)
    
    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 225), wall)
        for pellet in self.pellets:
            pygame.draw.ellipse(screen, (255, 255, 255), pellet)
            
        
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = speed
        self.dir = pygame.math.Vector2(0, 0) #Current Direction
        
    def move(self, dx, dy, walls):
        new_rect = self.rect.move(dx * self.speed, dy * self.speed)
            # Simple wall collision: shouldn't move if we would hit a wall
        for wall in walls:
            if new_rect.colliderect(wall):
                return
        self.rect = new_rect
    def collides_with(self, other):
        return self.rect.colliderect(other.rect)


class Ghost(Character):
    def handle_input(self, keys, walls):
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
            
        if dx != 0 or dy != 0:
            self.dir.update(dx, dy)
            self.move_grid(walls)

    def move_grid(self, walls):
        new_rect = self.rect.move(self.dir.x * TILE_SIZE, self.dir.y * TILE_SIZE)
        for wall in walls:
            if new_rect.colliderect(wall):
                return
        self.rect = new_rect


class Pacman(Character):
    def __init__(self, x, y, color, speed):
        super().__init__(x, y, color, speed)
        self.dir = pygame.math.Vector2(1, 0) #Start moving right
    
    def possible_directions(self,walls):
        dirs = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_rect = self.rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
            blocked = any(new_rect.colliderect(wall) for wall in walls)
            if not blocked:
                dirs.append(pygame.math.Vector2(dx, dy))
        return dirs
    
    def choose_direction(self, walls):
        options = self.possible_directions(walls)
        if not options:
            return pygame.math.Vector2(0,0)
        #If only one way to go, take it
        if len(options) == 1:
            return options[0]
        #If can keep going straight, do it
        #Remove the exact opposite direction to prevent continuos backtracking
        opposite = pygame.math.Vector2(-self.dir.x, -self.dir.y)
        options = [d for d in options if d != opposite] or options
        #At an intersection, prefer straight but sometimes turn
        straight_options = [d for d in options if d == self.dir]
        if straight_options and random.random() < 0.7: #70% chance to keep straight
            return self.dir
        #Otherwise choose remaining options (turn)
        return random.choice(options) 
    
    def update_ai(self, walls):
        #Decide next direction and move one tile
        self.dir = self.choose_direction(walls)
        new_rect = self.rect.move(self.dir.x * TILE_SIZE, self.dir.y * TILE_SIZE)
        blocked = any(new_rect.colliderect(wall) for wall in walls)
        if not blocked:
            self.rect = new_rect

class Game:
    """High-level game controller: state, score, and drawing."""
    
    def __init__(self):
        self.level = Level(MAZE_LAYOUT)
        if not self.level.ghost_starts or self.level.pacman_start is None:
            raise ValueError("Maze layout must have at least one ghost start (G) and one pacman start (P).")
        
        ghost_start = self.level.ghost_starts[0]
        pac_start = self.level.pacman_start
        
        self.ghost = Ghost(*ghost_start, GHOST_COLOR, speed=2)
        self.pacman = Pacman(*pac_start, PACMAN_COLOR, speed=3)
        self.sprites = pygame.sprite.Group(self.ghost, self.pacman)
        
        self.catches = 0
        self.pacman_timer = 0
        self.pacman_step_delay = 200 #ms between
        
        #Game state: "start", "playing", "won", "lost"
        self.state = "start"
        self.max_catches_to_win = 3
        
    def reset_round(self):
        """Reset positions after a catch without resetting score."""
        self.ghost.rect.topleft = self.level.ghost_starts[0]
        self.pacman.rect.topleft = self.level.pacman_start
        self.pacman_timer = 0
        
    def reset_game(self):
        """Reset entire game: score and positions."""
        self.catches = 0
        self.state = "playing"
        self.reset_round()
        
    def update(self, dt):
        if self.state != "playing":
            return
        
        self.pacman_timer += dt
        
        keys = pygame.key.get_pressed()
        self.ghost.handle_input(keys, self.level.walls)
        
        if self.pacman_timer >= self.pacman_step_delay:
            self.pacman.update_ai(self.level.walls)
            self.pacman_timer = 0
        
        #Pac-Man eats the pellets he touches
        for pellet in self.level.pellets[:]:
            if self.pacman.rect.colliderect(pellet):
                self.level.pellets.remove(pellet)
            
        #Collisions: ghost catches Pac-Man
        if self.ghost.collides_with(self.pacman):
            self.catches += 1
            if self.catches >= self.max_catches_to_win:
                self.state = "won"
            else:
                self.reset_round()
                
        #Lose condition: Pac-Man eats all pellets
        if not self.level.pellets:
            self.state = "lost"
            
    def draw(self, screen, font):
        screen.fill(BG_COLOR)
        
        if self.state == "start":
            title = font.render("Pac-Hunt: Press SPACE to start", True, (255, 255, 255))
            info = font.render("You are the ghost. Catch Pac-Man!", True, (255, 255, 255))
            screen.blit(title, (40, HEIGHT // 2 - 20))
            screen.blit(info, (80, HEIGHT // 2 + 10))
            return
        
        self.level.draw(screen)
        self.sprites.draw(screen)
        
        text = font.render(f"Catches: {self.catches}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        if self.state == "won":
            msg = font.render("You WON! Press R to restart.", True, (0, 255, 0))
            screen.blit(msg, (80, HEIGHT // 2))
        elif self.state == "lost":
            msg = font.render("You LOST! Press R to restart.", True, (255, 0, 0))
            screen.blit(msg, (80, HEIGHT // 2))
            

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Hunt")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    try:
        game = Game()
    except ValueError as e:
        print(e)
        pygame.quit()
        sys.exit()
        
    running = True
    while running:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if game.state == "start" and event.key == pygame.K_SPACE:
                    game.state = "playing"
                #From won/lost state, allow restart with R key
                elif game.state in ["won", "lost"] and event.key == pygame.K_r:
                    game.reset_game()
                    
        game.update(dt)
        game.draw(screen, font)
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()
    
    
if __name__ == "__main__":
    main()