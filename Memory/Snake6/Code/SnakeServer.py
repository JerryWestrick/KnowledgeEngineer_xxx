# Server Implementation for Process Online Game

import asyncio
from aiohttp import web
from typing import List

# Constants
from Snake_Constants import BOARD_SIZE, SNAKE_CHARACTERS, FOOD_CHAR, FOOD_COUNT, DIRECTION

# Initialize the game state
GameStatus = {
    "game_board": " " * (BOARD_SIZE * BOARD_SIZE),
    "free_snake_chars": SNAKE_CHARACTERS[:],
    "foods": [],
    "clients": {}
}

async def start_server(host: str, port: int):
    """Start the Process game server.

    Parameters:
        host (str): The hostname to bind the server to.
        port (int): The port number to listen for connections.
    """
    # Initialize the aiohttp web application
    app = web.Application()
    # Define routes for serving the client HTML and handling WebSocket connections
    app.router.add_get('/', serve_client_html)
    app.router.add_get('/ws', websocket_handler)
    # Run the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    # Keep the server running
    print(f'Process game server started on {host}:{port}')
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
    except asyncio.CancelledError:
        # Shutdown the server
        await runner.cleanup()

async def serve_client_html(request):
    """Serve the SnakeClient.html file to clients.

    Parameters:
        request: The request object.
    """
    # Read and return the content of SnakeClient.html
    content = open('SnakeClient.html', 'rb').read()
    return web.Response(body=content, content_type='text/html')

async def websocket_handler(request):
    """Handle WebSocket connections and messages.

    Parameters:
        request: The request object.
    """
    # Create a WebSocket response
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Add the WebSocket to the list of clients
    GameStatus['clients'][ws] = {'username': None, 'char': None, 'snake': [], 'score': 0, 'direction': 'Stop'}

    # Process incoming messages
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            # Handle text messages
            await process_client_message(ws, msg.data)
        elif msg.type == web.WSMsgType.ERROR:
            # Handle errors
            print(f'WebSocket connection closed with exception {ws.exception()}')

    # Remove the client from the game state when the WebSocket is closed
    del GameStatus['clients'][ws]
    print(f'WebSocket connection closed')

    return ws

def initialize_game_board() -> List[List[str]]:
    """Initialize the game board for the Process game.

    Returns:
        List[List[str]]: The initialized game board.
    """
    # Create a 100x100 2D list filled with spaces to represent the game board
    return [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def update_game_board(game_board: List[List[str]], game_state: dict):
    """Update the game board with the positions of snakes and food.

    Parameters:
        game_board (List[List[str]]): The game board to update.
        game_state (dict): The current game state.
    """
    # Iterate over the game state and update the game board accordingly
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            game_board[y][x] = ' '  # Clear the board

    # Place food on the board
    for food in game_state['foods']:
        x, y = food
        game_board[y][x] = FOOD_CHAR

    # Place snakes on the board
    for client in game_state['clients'].values():
        for segment in client['snake']:
            x, y = segment
            game_board[y][x] = client['char']

async def game_tick(game_state: dict):
    """Perform one tick of the game logic.

    Parameters:
        game_state (dict): The current game state.
    """
    # Update the game state for each tick
    for client_ws, client_info in game_state['clients'].items():
        if client_info['direction'] != 'Stop':
            # Calculate new head position
            head_x, head_y = client_info['snake'][0]
            dir_x, dir_y = DIRECTION[client_info['direction']]
            new_head = (head_x + dir_x, head_y + dir_y)

            # Check for collisions and handle snake death or food consumption
            # This is a simplified version and needs to be expanded with full game logic
            if new_head in game_state['foods']:
                # Eat food and grow
                client_info['snake'].insert(0, new_head)
                game_state['foods'].remove(new_head)
                client_info['score'] += 100
            elif 0 <= new_head[0] < BOARD_SIZE and 0 <= new_head[1] < BOARD_SIZE:
                # Move snake
                client_info['snake'].insert(0, new_head)
                client_info['snake'].pop()
                client_info['score'] += 1
            else:
                # Process dies
                await handle_snake_death(client_ws, game_state)

    # Update the game board
    update_game_board(game_state['game_board'], game_state)

    # Broadcast the new game state
    await broadcast_game_status(game_state)

    # Schedule the next tick
    asyncio.get_event_loop().call_later(0.2, asyncio.create_task, game_tick(game_state))

async def handle_client_joining(websocket, username: str, game_state: dict):
    """Handle a new client joining the game.

    Parameters:
        websocket: The WebSocket connection of the client.
        username (str): The username of the client.
        game_state (dict): The current game state.
    """
    # Assign a character to the client and initialize their snake
    if not game_state['free_snake_chars']:
        # No more characters available, close the connection
        await websocket.close()
        return

    client_char = game_state['free_snake_chars'].pop()
    game_state['clients'][websocket] = {
        'username': username,
        'char': client_char,
        'snake': [],  # Process will be initialized in reset_client
        'score': 0,
        'direction': 'Stop'
    }

    # Reset the client to start the game
    await reset_client(websocket, game_state)

async def handle_client_disconnect(websocket, game_state: dict):
    """Handle a client disconnecting from the game.

    Parameters:
        websocket: The WebSocket connection of the client.
        game_state (dict): The current game state.
    """
    # Remove the client from the game state and return their character to the pool
    client_info = game_state['clients'].get(websocket)
    if client_info:
        # Return the character to the pool of available characters
        game_state['free_snake_chars'].append(client_info['char'])
        # Remove the client's snake from the game board
        for segment in client_info['snake']:
            x, y = segment
            game_state['game_board'][y][x] = ' '
        # Remove the client from the game state
        del game_state['clients'][websocket]
        print(f'Client {client_info['username']} disconnected')

async def handle_snake_death(websocket, game_state: dict):
    """Handle the death of a snake.

    Parameters:
        websocket: The WebSocket connection of the client.
        game_state (dict): The current game state.
    """
    # Send a SnakeDied message to the client and reset their state
    await websocket.send_json({'type': 'SnakeDied', 'username': game_state['clients'][websocket]['username']})
    # Reset the client
    await reset_client(websocket, game_state)

def place_food_items(game_board: List[List[str]], game_state: dict):
    """Place food items on the game board.

    Parameters:
        game_board (List[List[str]]): The game board to place food on.
        game_state (dict): The current game state.
    """
    # Randomly place food items on the game board
    import random
    for _ in range(FOOD_COUNT):
        while True:
            x, y = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
            if game_board[y][x] == ' ':
                game_board[y][x] = FOOD_CHAR
                game_state['foods'].append((x, y))
                break

async def run_http_server(host: str, port: int):
    """Run the HTTP server to serve SnakeClient.html.

    Parameters:
        host (str): The hostname to bind the server to.
        port (int): The port number to listen for connections.
    """
    # Start the HTTP server using aiohttp
    app = web.Application()
    app.router.add_static('/', 'SnakeClient.html')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f'HTTP server running on {host}:{port}')

async def broadcast_game_status(game_state: dict):
    """Broadcast the game status to all connected clients.

    Parameters:
        game_state (dict): The current game state.
    """
    # Send the current game state to all connected clients
    for client_ws in game_state['clients']:
        await client_ws.send_json({
            'type': 'GameStatus',
            'game_board': game_state['game_board'],
            'clients': game_state['clients']
        })

async def handle_errors(websocket, error: Exception):
    """Handle errors during WebSocket communication.

    Parameters:
        websocket: The WebSocket connection of the client.
        error (Exception): The exception that occurred.
    """
    # Log the error and close the WebSocket connection
    print(f'Error: {error}')
    if not websocket.closed:
        await websocket.close()

def log_event(event_type: str, details: str):
    """Log an event in the game.

    Parameters:
        event_type (str): The type of event.
        details (str): The details of the event.
    """
    # Log the event with a timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] {event_type}: {details}')

# Additional server code and logic will be added here
