import pygame
import os

# 1. Asset Path Configuration 
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

# Main Game Loop
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    clock.tick(60)  # Limit the frame rate to 60 FPS
    screen.fill((0, 0, 0))  # Clear the screen with black
    pygame.display.flip()  # Update the display
    
pygame.quit()