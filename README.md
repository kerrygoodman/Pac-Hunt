# Pac-Hunt
My 2D game of Pac-Man with a twist. Instead of playing as Pac and running, you are the ghosts and are trying to catch Pac-Man.
# Pac-Hunt: The Ghosts Strike Back

Pac-Hunt is a Python/Pygame maze game where you **play as the ghost** hunting Pac-Man instead of the other way around. Your goal is to catch Pac-Man a set number of times before he manages to eat all the pellets in the maze.

This project was built as a 2D game development assignment using Python and the Pygame library.

### Requirements

- Python 3.11+ installed on your system
- Pygame installed in your environment

The game window titled **"Pac-Hunt: The Ghosts Strike Back"** should appear.

---

## Game Overview

### Core concept

- Classic Pac-Man style maze with walls and pellets laid out on a grid.
- You control a ghost; Pac-Man is controlled by simple AI.
- The win/loss condition is reversed:
  - You **win** by catching Pac-Man a set number of times.
  - You **lose** if Pac-Man eats all the pellets before you reach that number.

This “role reversal” twist is the main design change from the original Pac-Man and is central to the project’s mechanics.

### Game states

The game has several states managed by a `Game` class:

- `start`: shows a title and instructions; waits for player input.
- `playing`: normal gameplay.
- `won`: ghost has caught Pac-Man enough times.
- `lost`: Pac-Man has eaten all pellets.

## Controls

During gameplay:

- Arrow keys:
  - `←` move ghost left one tile
  - `→` move ghost right one tile
  - `↑` move ghost up one tile
  - `↓` move ghost down one tile

Menu / state controls:

- `SPACE` on the start screen:
  - Begin the game (switch from `"start"` to `"playing"`).
- `R` when the game is over:
  - Restart the game after a win or loss.
- Window close button:
  - Quits the game.

### Roles

- **Ghost (Player)**
  - You move on a grid, one tile at a time, and collide with walls.
  - Your objective is to intercept Pac-Man and “catch” him.
- **Pac-Man (AI)**
  - Moves automatically along the maze, also on the grid.
  - Tries to keep moving in the same direction if possible, but can turn at intersections.
  - Eats pellets whenever he touches them.
  - If he eats every pellet in the maze, you lose.

### Pellets
- Pellets are small white circles placed along open paths.
- When Pac-Man’s rectangle overlaps a pellet rectangle, that pellet is removed from the level.
- If the list of pellets becomes empty, the game state switches to `"lost"`.

### Winning and losing

- Catching Pac-Man:
  - If the ghost’s rectangle collides with Pac-Man’s rectangle, this counts as a “catch”.
  - The catch counter increases.
  - If the counter reaches `max_catches_to_win` (currently 3), the state becomes `"won"`.
  - Otherwise, the round resets: both characters return to their spawn positions and pellets are respawned.

- Pac-Man victory:
  - If Pac-Man eats all pellets before you reach the required number of catches, the state becomes `"lost"`.

### `Level`
- Responsible for building and drawing the maze.
- Uses `MAZE_LAYOUT`, a list of strings defining:
  - Walls (`W`)
  - Pellets (`.`)
  - Ghost spawn positions (`G`)
  - Pac-Man spawn position (`P`)
- Methods:
  - `__init__(layout)`: calls `build_level_from_layout` to create:
    - `walls`: list of wall rectangles
    - `pellets`: list of pellet rectangles
    - `ghost_starts`: ghost starting positions
    - `pacman_start`: Pac-Man starting position
    - `initial_pellets`: a copy used to respawn pellets each round
  - `draw(screen)`: draws all walls and pellets.

### `Character` (base class)

- Inherits from `pygame.sprite.Sprite`.
- Represents any movable character on the grid.
- Attributes:
  - `image`: a Pygame surface (sprite image or colored box).
  - `rect`: the rectangle used for position and collision.
  - `speed`: movement speed.
  - `dir`: a 2D vector for the current direction.
- Methods:
  - `move(dx, dy, walls)`: attempts to move; checks and prevents wall collisions.
  - `collides_with(other)`: returns `True` if the rectangles overlap.

### `Ghost` (player-controlled)

- Inherits from `Character`.
- Uses a ghost sprite image loaded via `load_sprite("ghost.png", TILE_SIZE)`.
- Methods:
  - `__init__`: sets the ghost image and starting position.
  - `handle_input(keys, walls)`:
    - Reads arrow keys.
    - Sets direction.
    - Calls `move_grid(walls)` to move one tile at a time.
  - `move_grid(walls)`:
    - Moves exactly one tile in the current direction if no wall blocks the way.

### `Pacman` (AI-controlled)

- Inherits from `Character`.
- Uses a Pac-Man sprite image loaded via `load_sprite("pacman.png", TILE_SIZE)`.
- Methods:
  - `possible_directions(walls)`:
    - Returns a list of directions (up/down/left/right) that are not blocked by walls.
  - `choose_direction(walls)`:
    - Chooses a direction based on:
      - Available options.
      - Avoiding immediate reversal.
      - Usually continuing straight, but sometimes turning at intersections (for less predictable movement).
  - `update_ai(walls)`:
    - Updates `dir` via `choose_direction`.
    - Moves one tile if the path is clear.

### `Game` (main controller)
- Manages the entire game state, score, and transitions.
- Attributes:
  - `ghost`, `pacman`: character instances.
  - `sprites`: a `pygame.sprite.Group` holding the characters.
  - `catches`: number of times the ghost has caught Pac-Man.
  - `pacman_timer`: time accumulator used to step Pac-Man’s movement at regular intervals.
  - `pacman_step_delay`: delay (in ms) between Pac-Man moves.
  - `state`: `"start"`, `"playing"`, `"won"`, or `"lost"`.
  - `max_catches_to_win`: number of catches required to win (currently 3).
- Methods:
  - `reset_round()`: resets ghost and Pac-Man positions and timer, and respawns pellets from `initial_pellets`.
  - `reset_game()`: resets score and state, then calls `reset_round()`.
  - `update(dt)`:
    - Responds to input for the ghost.
    - Updates Pac-Man’s AI movement on a timer.
    - Handles pellet eating by Pac-Man.
    - Checks collision between ghost and Pac-Man.
    - Updates game state to `"won"` or `"lost"` when conditions are met.
  - `draw(screen, font)`:
    - Clears the screen.
    - Draws the start screen if in `"start"` state.
    - Otherwise draws the level, sprites, and HUD (catches).
    - Displays win/lose messages when appropriate.

## Assets
- All art assets are expected in `src/assets/`:
  - `ghost.png`: sprite used for the ghost.
  - `pacman.png`: sprite used for Pac-Man.

## Design Choices

- **Role reversal**: Putting the player in control of the ghost flips the original game’s roles and forces a new strategy.
- **Grid-based movement**: Both characters move on a fixed tile grid, which simplifies collision detection and maze logic.
- **AI behavior**:
  - Pac-Man prefers to keep moving straight but can turn at intersections.
  - This keeps his path somewhat unpredictable but still understandable.

## How This Meets the Project Requirements
- Uses **Python and Pygame** for a 2D game. 
- Employs **object-oriented design** with multiple classes (`Game`, `Level`, `Character`, `Ghost`, `Pacman`).
- Implements a **meaningful twist** on a classic game (you play as the ghost hunting Pac-Man).
- Includes **clear controls**, **win/lose conditions**, and a **start screen**.
- Separates **game logic** (movement, collisions, state) from **rendering** (draw methods and sprite images).