# Process Game Code

# Import necessary libraries
import random
import curses

# Initialize the screen
s = curses.initscr()
curses.curs_set(0)
sh, sw = s.getmaxyx()
w = curses.newwin(sh, sw, 0, 0)
w.keypad(1)
w.timeout(100)

# Process initial position
snk_x = sw//4
snk_y = sh//2
snake = [
    [snk_y, snk_x],
    [snk_y, snk_x-1],
    [snk_y, snk_x-2]
]

# Process initial food position
food = [sh//2, sw//2]
w.addch(int(food[0]), int(food[1]), curses.ACS_PI)

# Initial snake direction
key = curses.KEY_RIGHT

# Function to get next position based on current direction
def next_position(key, current_head):
    """Calculate the next position of the snake's head.

    :param key: The current key indicating the direction
    :param current_head: The current position of the snake's head
    :return: The next position of the snake's head
    """
    y, x = current_head
    if key == curses.KEY_DOWN:
        y += 1
    elif key == curses.KEY_UP:
        y -= 1
    elif key == curses.KEY_LEFT:
        x -= 1
    elif key == curses.KEY_RIGHT:
        x += 1
    return y, x

# Main game loop
while True:
    next_key = w.getch()
    key = key if next_key == -1 else next_key

    new_head = next_position(key, snake[0])

    # Check for collision with borders
    if new_head[0] in [0, sh] or new_head[1]  in [0, sw] or new_head in snake:
        curses.endwin()
        quit()

    snake.insert(0, new_head)

    # Check if snake got the food
    if snake[0] == food:
        food = None
        while food is None:
            nf = [
                random.randint(1, sh-1),
                random.randint(1, sw-1)
            ]
            food = nf if nf not in snake else None
        w.addch(food[0], food[1], curses.ACS_PI)
    else:
        tail = snake.pop()
        w.addch(int(tail[0]), int(tail[1]), ' ')

    w.addch(int(snake[0][0]), int(snake[0][1]), curses.ACS_CKBOARD)
