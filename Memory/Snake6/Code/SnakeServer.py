# SnakeServer.py

import asyncio
from aiohttp import web

# 1. Python 3 and Async IO
async def start_server(host: str, port: int):
    """Initialize the main server coroutine and start the event loop."""
    loop = asyncio.get_event_loop()
    server = await web.ServerRunner(web.AppRunner(app))
    await server.setup()
    site = web.TCPSite(server, host, port)
    await site.start()
    print(f'Server started at http://{host}:{port}')
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await server.shutdown()
        await server.cleanup()
        loop.close()
        print('Server shutdown')

# 2. aiohttp Web Server
async def initialize_web_server(app):
    """Create an aiohttp web application and set up routes."""
    app.router.add_get('/', serve_client_html)
    app.router.add_static('/static/', path='static', name='static')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print('Web server started on http://localhost:8080')

# 3. Websocket Support
async def websocket_handler(request):
    """Upgrade the HTTP request to a websocket connection and handle messages."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app['websockets'].add(ws)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await handle_message(ws, msg.json())
            elif msg.type == web.WSMsgType.ERROR:
                print('ws connection closed with exception', ws.exception())
    finally:
        request.app['websockets'].discard(ws)

    print('websocket connection closed')
    return ws

# 4. Game Board Management
def update_game_board(game_state):
    """Iterate over the game board and update the positions of snakes and food."""
    board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for food in game_state['foods']:
        x, y = food
        board[y][x] = FOOD_CHAR
    for client in game_state['clients'].values():
        for segment in client['snake']:
            x, y = segment
            board[y][x] = client['char']
    game_state['game_board'] = '\n'.join(''.join(row) for row in board)

# 5. Game Tick Logic
async def process_game_tick(game_state):
    """Handle the logic for each game tick, including movement and collision."""
    while True:
        update_game_board(game_state)
        for client_id, client in game_state['clients'].items():
            if client['direction'] != 'Stop':
                manage_snake_lifecycle(client_id)
        await broadcast_game_status(game_state)
        await asyncio.sleep(0.2)  # 5 ticks per second

# 6. Collision Detection
def check_collision(position: tuple, game_state) -> bool:
    """Check if the given position collides with boundaries, snakes, or food."""
    x, y = position
    if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
        return True  # Collision with boundary
    for client in game_state['clients'].values():
        if position in client['snake']:
            return True  # Collision with snake
    return False  # No collision

# 7. Snake Lifecycle Management
def manage_snake_lifecycle(client_id, game_state):
    """Handle the creation, movement, and death of a client's snake."""
    client = game_state['clients'][client_id]
    head_x, head_y = client['snake'][0]
    move_x, move_y = DIRECTION[client['direction']]
    new_head = (head_x + move_x, head_y + move_y)
    if check_collision(new_head, game_state):
        reset_client(client_id, game_state)
        return
    client['snake'].insert(0, new_head)  # Move snake by adding new head
    if new_head in game_state['foods']:
        game_state['foods'].remove(new_head)
        manage_food(game_state)
        client['score'] += 100
    else:
        client['snake'].pop()  # Remove tail if not eating

# 8. Food Management
def manage_food(game_state):
    """Place new food items on the game board when consumed."""
    from random import randint
    while len(game_state['foods']) < FOOD_COUNT:
        x, y = randint(0, BOARD_SIZE - 1), randint(0, BOARD_SIZE - 1)
        if (x, y) not in game_state['foods'] and not any((x, y) in client['snake'] for client in game_state['clients'].values()):
            game_state['foods'].append((x, y))

# 9. Client Management
async def manage_client(websocket, game_state):
    """Handle client joining, disconnection, and maintain their game state."""
    try:
        async for message in websocket:
            data = message.json()
            if data['type'] == 'Joining':
                handle_username(websocket, data['username'], game_state)
            elif data['type'] == 'DirectionChange':
                game_state['clients'][websocket]['direction'] = data['direction']
    except web.WebSocketException as e:
        handle_error(e)
    finally:
        client_id = websocket
        if client_id in game_state['clients']:
            del game_state['clients'][client_id]
            assign_client_character(client_id, game_state)

# 10. Score Tracking
def update_scores(client_id, points: int, game_state):
    """Update the score of the specified client by the given points."""
    if client_id in game_state['clients']:
        game_state['clients'][client_id]['score'] += points

# 11. Client Communication
async def broadcast_game_status(game_state):
    """Serialize the current game status and send it to all connected clients."""
    game_status_message = {
        'type': 'GameStatus',
        'game_board': game_state['game_board'],
        'clients': {client_id: {'char': client['char'], 'score': client['score']} for client_id, client in game_state['clients'].items()}
    }
    for ws in game_state['websockets']:
        await ws.send_json(game_status_message)

# 12. Error Handling
def handle_error(error, game_state):
    """Log the error and perform any necessary cleanup or state reset."""
    print(f'Error: {error}')
    # Perform necessary cleanup related to the error
    # This could involve resetting game state, removing clients, etc.
    # Specific cleanup actions depend on the error context

# 13. Resource Management
def manage_resources(game_state):
    """Monitor and optimize the usage of game resources."""
    # This function would contain logic to manage and optimize resources
    # For example, it could handle memory management, connection pooling, etc.
    # Currently, this is a placeholder as the specifics depend on game requirements and infrastructure

# 14. HTTP Server Startup
async def serve_client_html(request):
    """Serve the SnakeClient.html file in response to HTTP GET requests."""
    return web.FileResponse('SnakeClient.html')

# 15. Client Character Assignment
def assign_client_character(client_id, game_state):
    """Assign a unique character to a new client from the available pool."""
    if game_state['free_snake_chars']:
        game_state['clients'][client_id]['char'] = game_state['free_snake_chars'].pop(0)
    else:
        raise ValueError('No more characters available to assign.')

# 16. Client Reset
def reset_client(client_id, game_state):
    """Reset the client's snake to a default state."""
    from random import randint
    while True:
        x = randint(0, BOARD_SIZE - 3)
        y = randint(0, BOARD_SIZE - 1)
        snake = [(x, y), (x, y+1), (x, y+2)]
        if all(check_collision(segment, game_state) == False for segment in snake):
            break
    game_state['clients'][client_id]['snake'] = snake
    game_state['clients'][client_id]['score'] = 0
    game_state['clients'][client_id]['direction'] = 'Stop'
    for segment in snake:
        x, y = segment
        game_state['game_board'][y][x] = game_state['clients'][client_id]['char']

# 17. Client Username Handling
def handle_username(client_id, username: str, game_state):
    """Associate a unique username with the client's snake character."""
    if username in (client['name'] for client in game_state['clients'].values()):
        raise ValueError('Username already taken.')
    game_state['clients'][client_id]['name'] = username

# 18. Client Score Display
def display_client_scores(game_state) -> str:
    """Create a string representation of the client list with scores."""
    return ' '.join(f'{client["char"]}{client["name"]}:{client["score"]}' for client in game_state['clients'].values())

# 19. Message Handling
async def handle_message(websocket, message: dict, game_state):
    """Parse and handle different types of incoming messages."""
    message_type = message.get('type')
    if message_type == 'Joining':
        await manage_client(websocket, message['username'], game_state)
    elif message_type == 'DirectionChange':
        client_id = websocket  # Assuming websocket is used as client_id
        if client_id in game_state['clients']:
            game_state['clients'][client_id]['direction'] = message['direction']
    elif message_type == 'SnakeDied':
        client_id = websocket  # Assuming websocket is used as client_id
        reset_client(client_id, game_state)

# 20. Security
def enforce_security(message: dict, game_state):
    """Implement security measures to prevent cheating and unauthorized access."""
    # Example security checks (to be expanded as needed):
    # - Check if the message type is valid
    # - Check if the message comes from a known and active client
    # - Rate limiting to prevent spamming
    # - Validate message content to prevent injection attacks
    if message.get('type') not in ['Joining', 'DirectionChange', 'SnakeDied']:
        raise ValueError('Invalid message type.')
    if 'client_id' in message and message['client_id'] not in game_state['clients']:
        raise ValueError('Unknown client.')
