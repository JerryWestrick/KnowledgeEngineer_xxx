import asyncio
from aiohttp import web

# 1. Python 3 and Async IO
async def start_server(host: str, port: int):
    """Initialize the main server coroutine and set up the event loop."""
    app = web.Application()
    app.router.add_get('/', serve_client_html)
    app.router.add_get('/ws', websocket_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f'Server started at http://{host}:{port}')
    try:
        while True:
            await asyncio.sleep(3600)  # Run forever
    except asyncio.CancelledError:
        pass  # Server is stopped
    finally:
        await runner.cleanup()

# 2. aiohttp Web Server
async def serve_client_html(request):
    """Serve the SnakeClient.html file in response to HTTP GET requests."""
    return web.FileResponse('SnakeClient.html')

# 3. WebSockets Support
async def websocket_handler(request):
    """Manage WebSocket connections and process messages from clients."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app['websockets'].add(ws)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await process_client_message(msg.json(), ws)
            elif msg.type == web.WSMsgType.ERROR:
                print('WebSocket connection closed with exception', ws.exception())
    finally:
        request.app['websockets'].discard(ws)

    return ws

# 4. Game Board Management
def update_game_board(snake_positions, food_positions):
    """Update the game board with the positions of snakes and food."""
    # Clear the game board
    game_board = [' ' * BOARD_SIZE for _ in range(BOARD_SIZE)]
    # Place food on the game board
    for food in food_positions:
        x, y = food
        game_board[y][x] = FOOD_CHAR
    # Place snakes on the game board
    for snake in snake_positions:
        for segment in snake:
            x, y = segment
            game_board[y][x] = SNAKE_CHAR
    # Convert the game board to a single string
    return '\n'.join(''.join(row) for row in game_board)

# 5. Game Ticks
async def game_tick():
    """Perform actions associated with a single game tick."""
    while True:
        # Update the game board
        update_game_board(GameStatus['clients'].values(), GameStatus['foods'])
        # Move each snake
        for client in GameStatus['clients'].values():
            move_snake(client['snake'], DIRECTION[client['direction']])
        # Broadcast the new game status
        await broadcast_game_status()
        # Wait for the next tick
        await asyncio.sleep(0.2)  # Game tick rate is 5 per second

# 6. Snake Movement and Collision Detection
def move_snake(snake, direction):
    """Move a snake on the game board and detect collisions."""
    head_x, head_y = snake[0]
    dir_x, dir_y = direction
    new_head = (head_x + dir_x, head_y + dir_y)

    # Check for collisions with walls
    if new_head[0] < 0 or new_head[0] >= BOARD_SIZE or new_head[1] < 0 or new_head[1] >= BOARD_SIZE:
        raise Exception('Snake hit the wall')

    # Check for collisions with itself
    if new_head in snake:
        raise Exception('Snake ran into itself')

    # Move the snake
    snake.insert(0, new_head)
    snake.pop()

# 7. Score and Food Management
def manage_food_and_score(snake, new_head_position):
    """Handle scoring and food distribution on the game board."""
    # Check if the snake's new head position is on a food
    if new_head_position in GameStatus['foods']:
        # Increase the score
        snake['score'] += 100
        # Add a new segment to the snake
        snake['snake'].insert(0, new_head_position)
        # Remove the eaten food
        GameStatus['foods'].remove(new_head_position)
        # Add new food to the game board
        add_food()
    else:
        # Move the snake normally
        snake['snake'].insert(0, new_head_position)
        snake['snake'].pop()
        # Increase the score slightly
        snake['score'] += 1

    # Function to add new food to the game board
    def add_food():
        while True:
            new_food_position = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
            if new_food_position not in GameStatus['foods'] and new_food_position not in snake['snake']:
                GameStatus['foods'].append(new_food_position)
                break

# 8. Client Management
def assign_snake_character(client):
    """Assign an available snake character to a new client."""
    if not GameStatus['free_snake_chars']:
        raise Exception('No more snake characters available')
    client['char'] = GameStatus['free_snake_chars'].pop(0)
    reset_client(client)

    def reset_client(client):
        # Reset the client's game state
        client['snake'] = [(random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)) for _ in range(3)]
        client['score'] = 0
        client['direction'] = 'Stop'
        # Draw the snake on the game board
        for position in client['snake']:
            x, y = position
            GameStatus['game_board'][y * BOARD_SIZE + x] = client['char']

# 9. Handling Client Messages
async def process_client_message(message, websocket):
    """Process messages received from clients."""
    message_data = json.loads(message)
    if message_data['type'] == 'Joining':
        await handle_joining(message_data, websocket)
    elif message_data['type'] == 'DirectionChange':
        await handle_direction_change(message_data, websocket)

    async def handle_joining(message_data, websocket):
        username = message_data['username']
        client = {'username': username, 'websocket': websocket}
        assign_snake_character(client)
        GameStatus['clients'][username] = client

    async def handle_direction_change(message_data, websocket):
        username = message_data['username']
        direction = message_data['direction']
        if username in GameStatus['clients']:
            GameStatus['clients'][username]['direction'] = direction

# 10. Client Disconnection
async def handle_client_disconnection(websocket):
    """Handle the disconnection of clients."""
    for username, client in GameStatus['clients'].items():
        if client['websocket'] == websocket:
            # Return the snake character to the pool
            GameStatus['free_snake_chars'].append(client['char'])
            # Remove the client's snake from the game board
            for position in client['snake']:
                x, y = position
                GameStatus['game_board'][y * BOARD_SIZE + x] = ' '
            # Remove the client from the game status
            del GameStatus['clients'][username]
            break

# 11. Sending Game Status
async def broadcast_game_status():
    """Send the current game status to all connected clients."""
    game_status_message = json.dumps({
        'type': 'GameStatus',
        'game_board': GameStatus['game_board'],
        'clients': GameStatus['clients']
    })
    for websocket in request.app['websockets']:
        await websocket.send_str(game_status_message)

# 12. HTTP Server Startup
async def initialize_http_server():
    """Start the HTTP server to serve the SnakeClient.html file."""
    app = web.Application()
    app.router.add_static('/', path=str(Path(__file__).parent), name='SnakeClient.html')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print('HTTP server started on http://localhost:8080')

# 13. Error Handling
def handle_exceptions(exception):
    """Manage exceptions and unexpected behavior."""
    print(f'An exception occurred: {exception}')
    # Here you can add any logging or cleanup tasks that are necessary
