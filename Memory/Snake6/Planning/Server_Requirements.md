Server Requirements

1. Architecture

The server side of the multi-user 'Snake' online game will be implemented in Python 3 using Async IO and aiohttp to serve the SnakeClient.html file and connect via websockets.

2. Game Board

The server will maintain a 100x100 2D character representation of the playing ground called the game_board. The game_board will be updated with the values of snakes and foods. Collisions can be checked by examining the character value in the game_board at a specific position.

3. Ticks Logic

The game will be implemented using ticks, with 5 ticks per second. Each tick will perform the following actions:

- Move each snake whose direction is not 'Stop'. If the new head position is out of bounds or collides with another snake, the snake dies.
- If the new head position contains a food, the snake eats it, increases its score, and a new food is randomly placed on the game_board.
- If the new head position is empty, the snake moves to the new position and its tail is updated.
- The updated game status is sent to all connected clients.

4. Snake Dies

When a snake dies, the server sends a SnakeDied message to the client, erases the client's snake from the game_board, and performs a reset for the client.

5. Reset A Client

When resetting a client, a new snake head is randomly positioned, the client's snake is updated, the client's score is set to zero, and the client's direction is set to 'Stop'.

6. Joining

When a client sends a 'Joining' message, the server assigns a character from the free_snake_chars list to the client, sets the client's username, and performs a reset for the client. If there are no available characters, the server closes the websocket.

7. Websocket Disconnect

When a websocket disconnects, the server returns the client's character to the free_snake_chars list, erases the client's snake from the game_board, and removes the client from the game_status.

8. Startup

At startup, the server starts an HTTP server to serve the SnakeClient.html file.
