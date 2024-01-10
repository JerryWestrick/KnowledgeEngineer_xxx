# Snake Game Implementation

import random
import curses


def initialize_screen():
    """Initializes the curses screen window.

    Returns:
        screen: The initialized curses screen window.
    """
    screen = curses.initscr()
    curses.curs_set(0)  # Hide the cursor
    screen.keypad(1)  # Enable keypad for the screen
    curses.noecho()  # Prevent input from displaying in the screen
    curses.cbreak()  # React to keys without requiring the Enter key
    screen.border(0)  # Create a border around the screen
    return screen


def create_game_window(screen):
    """Creates the window for the snake game.

    Args:
        screen: The curses screen window where the game will be displayed.

    Returns:
        win: The created game window within the screen.
    """
    sh, sw = screen.getmaxyx()  # Get screen height and width
    w = curses.newwin(sh, sw, 0, 0)  # Create a new window for the game
    w.keypad(1)  # Enable keypad for the game window
    w.timeout(100)  # Set the screen refresh timeout
    return w


def game_loop(win):
    """The main loop where the game logic is executed.

    Args:
        win: The game window where the game loop will run.
    """
    # Initial game settings
    snake = [(5, 10), (5, 9), (5, 8)]  # Initial snake
    food = generate_food(win, snake)  # Place initial food
    score = 0  # Initial score

    # Initial direction
    key = curses.KEY_RIGHT

    while True:
        key = handle_input(key, win)

        # Update snake position
        snake = update_snake_position(snake, key)

        # Check for collisions
        if check_collisions(snake, win):
            display_game_over(win)
            if restart_game(win):
                snake = [(5, 10), (5, 9), (5, 8)]
                food = generate_food(win, snake)
                score = 0
                key = curses.KEY_RIGHT
                continue
            else:
                break

        # Place new food or grow snake
        if snake[0] == food:
            score = update_score(score, win)
            food = grow_snake(snake, food, win)
        else:
            tail = snake.pop()
            win.addch(tail[0], tail[1], ' ')

        # Update score
        win.addstr(0, 2, 'Score: ' + str(score))

        # Refresh screen
        win.addch(food[0], food[1], '*')
        win.addch(snake[0][0], snake[0][1], '#')

        # End game if collision occurs
        # Already handled above


def handle_input(key, win):
    """Handles user input during the game.

    Args:
        key: The current key that indicates the snake's direction.
        win: The game window to listen for input.

    Returns:
        The new direction based on the player's input.
    """
    new_key = win.getch()
    key = key if new_key == -1 else new_key
    return key


def update_snake_position(snake, key):
    """Updates the position of the snake based on the current direction.

    Args:
        snake: A list of tuples representing the snake's body segments.
        key: An integer representing the current direction of the snake.

    Returns:
        new_head: A tuple representing the new position of the snake's head.
    """
    head = snake[0]
    if key == curses.KEY_DOWN:
        new_head = (head[0] + 1, head[1])
    elif key == curses.KEY_UP:
        new_head = (head[0] - 1, head[1])
    elif key == curses.KEY_LEFT:
        new_head = (head[0], head[1] - 1)
    elif key == curses.KEY_RIGHT:
        new_head = (head[0], head[1] + 1)
    snake.insert(0, new_head)
    return snake


def check_collisions(snake, win):
    """Checks for collisions with walls or the snake's body.

    Args:
        snake: A list of tuples representing the snake's body segments.
        win: The game window to check for wall boundaries.

    Returns:
        bool: True if a collision is detected, False otherwise.
    """
    sh, sw = win.getmaxyx()
    head = snake[0]
    if head[0] in [0, sh] or head[1]  in [0, sw] or head in snake[1:]:
        return True
    return False


def generate_food(win, snake):
    """Generates food in a random position within the game window.

    Args:
        win: The game window where the food will be placed.
        snake: A list of tuples representing the snake's body segments to avoid placing food on it.

    Returns:
        food: A tuple representing the position of the food.
    """
    sh, sw = win.getmaxyx()
    food = None
    while food is None:
        food = (random.randint(1, sh-1), random.randint(1, sw-1))
        if food in snake:
            food = None
    win.addch(food[0], food[1], '*')
    return food


def grow_snake(snake, food, win):
    """Grows the snake's length after consuming food.

    Args:
        snake: A list of tuples representing the snake's body segments.
        food: A tuple representing the position of the food.
        win: The game window where the snake is displayed.

    Returns:
        new_food: A tuple representing the position of the new food.
    """
    sh, sw = win.getmaxyx()
    tail = snake[-1]
    tail2 = snake[-2]
    if tail[0] == tail2[0]:  # Horizontal growth
        if tail[1] > tail2[1]:
            new_tail = (tail[0], tail[1] + 1)
        else:
            new_tail = (tail[0], tail[1] - 1)
    else:  # Vertical growth
        if tail[0] > tail2[0]:
            new_tail = (tail[0] + 1, tail[1])
        else:
            new_tail = (tail[0] - 1, tail[1])
    snake.append(new_tail)
    new_food = generate_food(win, snake)
    return new_food


def update_score(score, win):
    """Updates the game score after the snake consumes food.

    Args:
        score: The current score of the game.
        win: The game window where the score will be displayed.

    Returns:
        score: The updated score after consuming food.
    """
    score += 1
    win.addstr(0, 2, 'Score: ' + str(score))
    return score


def display_game_over(win):
    """Displays the game over screen.

    Args:
        win: The game window where the game over message will be displayed.
    """
    sh, sw = win.getmaxyx()
    msg = 'Game Over!'
    win.addstr(sh // 2, (sw // 2) - (len(msg) // 2), msg)
    win.nodelay(0)  # Make getch() wait for the user to press a key
    win.getch()  # Wait for user input before exiting the game over screen
    curses.endwin()  # Restore the terminal to its original operating mode


def restart_game(win):
    """Restarts the game after a game over.

    Args:
        win: The game window where the game will be restarted.

    Returns:
        bool: True if the game should be restarted, False otherwise.
    """
    win.clear()
    win.addstr(2, 2, 'Press R to Restart or Q to Quit')
    key = win.getch()
    if key == ord('r') or key == ord('R'):
        return True
    elif key == ord('q') or key == ord('Q'):
        return False
    else:
        return restart_game(win)


def main():
    """The main function to start the Snake game."""
    screen = initialize_screen()
    win = create_game_window(screen)
    game_loop(win)

if __name__ == '__main__':
    main()
