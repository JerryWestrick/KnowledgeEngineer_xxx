# Snake Game Implementation

# Import necessary libraries
import random
import curses

# Initialize the game

def init_game():
    """Initialize the game window and settings."""
    # Initialize curses
    stdscr = curses.initscr()
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Make stdscr.getch non-blocking
    stdscr.keypad(True)  # Enable special keys to be read as single values

    # Set up the window dimensions
    height, width = 20, 40  # Example dimensions
    win = curses.newwin(height, width, 0, 0)
    win.keypad(True)  # Enable keypad mode
    curses.noecho()  # Prevent input from being echoed
    curses.cbreak()  # React to keys without requiring the Enter key

    # Set up game variables
    snake = [(height//2, width//4)]  # Initial snake position
    snake_dir = curses.KEY_RIGHT  # Initial snake direction
    food = (height//2, width//2)  # Initial food position
    score = 0  # Initial score

    # Draw the game area
    draw_game_area(win)

    # Return the game state
    return {'win': win, 'snake': snake, 'snake_dir': snake_dir, 'food': food, 'score': score}

# Game loop

def game_loop(win, snake, snake_dir, food, score):
    """Run the main game loop.

    :param win: Curses window object
    :param snake: List of tuples representing the snake's body
    :param snake_dir: The current direction of the snake
    :param food: Tuple representing the food's position
    :param score: Integer representing the current score
    """
    # Set initial game state
    last_key = snake_dir

    while True:
        # Get user input
        next_key = win.getch()
        last_key = next_key if next_key != -1 else last_key

        # Update snake's direction based on user input
        if last_key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
            snake_dir = last_key

        # Move the snake
        move_snake(snake, snake_dir)

        # Check for collision
        if detect_collision(snake, win):
            game_over(score)
            break

        # Check if food is eaten
        if snake[0] == food:
            score += 1
            food = generate_food(win, snake)
            grow_snake(snake)
            update_score(win, score)
        else:
            # Move the snake
            tail = snake.pop()
            win.addch(int(tail[0]), int(tail[1]), ' ')

        # Render the snake and food
        win.addch(int(food[0]), int(food[1]), curses.ACS_PI)
        for segment in snake:
            win.addch(int(segment[0]), int(segment[1]), curses.ACS_CKBOARD)

        # Refresh the screen
        win.refresh()

        # Wait for the next tick
        speed = increase_difficulty(score)
        curses.napms(speed)

# Snake movement

def move_snake(snake, direction):
    """Move the snake in the specified direction.

    :param snake: List of tuples representing the snake's body
    :param direction: The current direction of the snake
    """
    head = snake[0]
    new_head = (head[0], head[1])

    if direction == curses.KEY_DOWN:
        new_head = (head[0] + 1, head[1])
    elif direction == curses.KEY_UP:
        new_head = (head[0] - 1, head[1])
    elif direction == curses.KEY_LEFT:
        new_head = (head[0], head[1] - 1)
    elif direction == curses.KEY_RIGHT:
        new_head = (head[0], head[1] + 1)

    snake.insert(0, new_head)

# Food generation

def generate_food(win, snake):
    """Randomly place a food item on the grid.

    :param win: Curses window object
    :param snake: List of tuples representing the snake's body
    :return: Tuple representing the new food position
    """
    height, width = win.getmaxyx()
    while True:
        food = (random.randint(1, height - 2), random.randint(1, width - 2))
        if food not in snake:
            return food

# Snake growth

def grow_snake(snake):
    """Increase the length of the snake after consuming food.

    :param snake: List of tuples representing the snake's body
    """
    # The snake grows by adding a segment in the same position as the last segment
    snake.append(snake[-1])

# Scoring system

def update_score(win, score):
    """Update the player's score on the screen.

    :param win: Curses window object
    :param score: The current score to be updated
    """
    # Display the score in the top right corner
    height, width = win.getmaxyx()
    score_text = 'Score: {}'.format(score)
    win.addstr(0, width - len(score_text) - 2, score_text)

# Collision detection

def detect_collision(snake, win):
    """Detect collision with walls or the snake's own body.

    :param snake: List of tuples representing the snake's body
    :param win: Curses window object
    :return: Boolean indicating whether a collision occurred
    """
    height, width = win.getmaxyx()
    head = snake[0]
    # Check if the snake has collided with the walls
    if head[0] in [0, height] or head[1]  in [0, width] or head in snake[1:]:
        return True
    return False

# Difficulty progression

def increase_difficulty(score):
    """Increase the game difficulty based on the score.

    :param score: The current score
    :return: The new speed of the game
    """
    # As an example, increase speed every 5 points
    speed = 100 - (score // 5) * 10
    speed = max(speed, 10)  # Set a minimum speed limit
    return speed

# User interface

def draw_game_area(win):
    """Draw the fixed-size grid for the game area.

    :param win: Curses window object
    """
    # Draw a border around the game area
    win.box()
    # Refresh the window to show the border
    win.refresh()

# Game over

def game_over(score):
    """Display the game over screen and final score.

    :param score: The final score
    """
    # Clear the screen
    curses.endwin()
    # Print the final score
    print('\nGame Over!\nYour final score was: {}'.format(score))

# Main function
if __name__ == '__main__':
    # Initialize and run the game
    game_state = init_game()
    game_loop(**game_state)
    curses.endwin()  # End curses mode
