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

SCREEN_Width = 640
SCREEN_Height = 480
screen = pygame.display.set_mode((SCREEN_Width, SCREEN_Height))
pygame.display.set_caption("Pac-Hunt: The Ghosts Strike Back")

#Game Loop Variables
clock = pygame.time.Clock()
running = True


class Game:
    def __init__(self):
        self.level = Level("level1.txt")
        self.ghosts = [Ghost(self.level.ghost_start)]
        self.pacman = Pacman(self.level.pacman_start)
        self.score = 0

    def update(self, dt):
        self.ghosts[0].update(dt, self.level)
        self.pacman.update(dt, self.level)
        if self.ghosts[0].collides_with(self.pacman):
            self.handle_catch()

    def draw(self, screen):
        self.level.draw(screen)
        self.pacman.draw(screen)
        for g in self.ghosts:
            g.draw(screen)
    def handle_catch(self):        print("Pacman caught! Game Over.")
        # Reset game or end it as needed  


# Game Constants
WIDTH, HEIGHT = 640, 480
FPS = 60
BG_COLOR = (0, 0, 0)
GHOST_COLOR = (0, 255, 255)
PACMAN_COLOR = (255, 255, 0)
TILE_SIZE = 32
# Maze Layout: each character is one TILE
# w = wall, . = pellet, ' ' = empty space, G = ghost start, P = pacman start
MAZE_LAYOUT = [
    "wwwwwwwwwwwwwwww",
    "w......W......Pw",
    "w.WWWW.W.WWWW.W.W",
    "W.W....W....W.W.w",
    "W.W.WWWWWW.WW.W.w",
    "w..............w",
    "w.W.WW.WWW.WW.W.W",
    "W.W..G.....G..W.W",
    "W.WWWW.W.WWWW.W.W",
    "W......W.......WW",
    "wwwwwwwwwwwwwwww"
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
                pellets.append(pygame.Rect(x + TILE_SIZE//4, y + TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
            elif ch == 'G':
                ghost_starts.append((x, y))
            elif ch == "P":
                pacman_start = (x, y)
    return walls, pellets, ghost_starts, pacman_start
        
    


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
        straight_ok = any(d == self.dir for d in options)
        if straight_ok:
            return self.dir
        if options:
            return random.choice(options)
        return pygame.math.Vector2(0,0)
    def update_ai(self, walls):
        self.dir = self.choose_direction(walls)
        new_rect = self.rect.move(self.dir.x * TILE_SIZE, self.dir.y * TILE_SIZE)
        blocked = any(new_rect.colliderect(wall) for wall in walls)
        if not blocked:
            self.rect = new_rect


def create_simple_maze():
    walls = []
    #Border walls
    for x in range(0, WIDTH, TILE_SIZE):
        walls.append(pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE))
        walls.append(pygame.Rect(x, HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for y in range(0, HEIGHT, TILE_SIZE):
        walls.append(pygame.Rect(0, y, TILE_SIZE, TILE_SIZE))
        walls.append(pygame.Rect(WIDTH - TILE_SIZE, y, TILE_SIZE, TILE_SIZE))
    return walls


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Hunt")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    walls, pellets, ghost_starts, pacman_start = build_level_from_layout(MAZE_LAYOUT)

    ghost = Ghost(*ghost_starts[0], GHOST_COLOR, speed=2)
    pacman = Pacman(*pacman_start, PACMAN_COLOR, speed=2)
    
    all_sprites = pygame.sprite.Group(ghost, pacman)
    
    catches = 0
    running = True
    while running:
        dt = clock.tick(FPS)
        pacman_timer += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        ghost.handle_input(keys, walls)
        
        if pacman_timer >= pacman_step_delay:
            pacman.update_ai(walls)
            pacman_timer = 0
            
        if ghost.rect.colliderect(pacman.rect):
            catches += 1 #Reset positions when you catch Pac-Man
            ghost.rect.topleft = ghost_starts[0]
            pacman.rect.topleft = pacman_start
            
        screen.fill(BG_COLOR)
        
        #Draw walls
        for wall in walls:
            pygame.draw.rect(screen, (0, 0, 225), wall)
        #Draw pellets
        for pellet in pellets:
            pygame.draw.ellipse(screen, (255, 255, 255), pellet)
            
        all_sprites.draw(screen)
        
        text = font.render(f"Catches: {catches}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()