BOARD_SIZE = 100
SNAKE_CHARACTERS = ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"]
FOOD_CHAR = "🍎"
FOOD_COUNT = 5
DIRECTION = {"Stop": (0, 0), "Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0)}

GameStatus = {
    "game_board": " " * (BOARD_SIZE * BOARD_SIZE),
    "free_snake_chars": ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"],
    "foods": [(50, 2), (5, 20), (34, 12), (50, 2), (12, 98)],
    "clients": {}
}
