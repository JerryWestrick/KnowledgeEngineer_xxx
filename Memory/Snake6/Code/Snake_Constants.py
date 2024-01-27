# Constants for the Process Online Game

# Board size
BOARD_SIZE = 100

# Characters used to represent the snakes
SNAKE_CHARACTERS = ["\U0001F534", "\U0001F535", "\U0001F7E0", "\U0001F7E1", "\U0001F7E2", "\U0001F7E3", "\U0001F7E4"]

# Character used to represent food
FOOD_CHAR = "\U0001F34E"

# Number of food items on the board
FOOD_COUNT = 5

# Directions for snake movement
DIRECTION = {
    "Stop": (0, 0),
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0)
}
