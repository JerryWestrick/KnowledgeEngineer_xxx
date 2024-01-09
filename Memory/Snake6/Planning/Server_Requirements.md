# Server Requirements for Snake Online Game

## Detailed Description of Each Requirement

### 1. Python 3 and Async IO
- The server must be implemented using Python 3.
- It should utilize asynchronous I/O operations to handle multiple client connections efficiently.

### 2. aiohttp Web Server
- The server should use the aiohttp library to serve the SnakeClient.html file.
- It must handle HTTP requests and serve static files required by the client.

### 3. WebSockets Support
- The server must support WebSocket connections for real-time communication with clients.
- It should manage multiple WebSocket connections concurrently.

### 4. Game Board Management
- The server must maintain a 100x100 2D character array representing the game board.
- It should update the game board with the positions of snakes and food items.
- The server must check for collisions by inspecting the character at a given position on the game board.

### 5. Game Ticks
- The server must implement game logic in ticks, with 5 ticks per second.
- Each tick involves moving snakes, checking for collisions, updating scores, and sending the updated game state to clients.

### 6. Snake Movement and Collision Detection
- The server must handle the movement of each snake based on its direction.
- It should detect collisions with the boundaries, other snakes, or food.
- The server must handle the death of a snake and its removal from the game board.

### 7. Food Mechanics
- The server should manage the placement and consumption of food items on the game board.
- It must generate new food items at random positions when consumed by a snake.

### 8. Score Management
- The server must keep track of each client's score.
- It should update scores when a snake consumes food or moves without dying.

### 9. Client Management
- The server must manage the list of connected clients and their corresponding snakes.
- It should handle client join requests, disconnections, and reassignments of snake characters.

### 10. Client Communication
- The server must send the updated game state to all connected clients after each tick.
- It should communicate with clients using predefined messages such as "Joining", "DirectionChange", and "SnakeDied".

### 11. Error Handling and Logging
- The server should handle errors gracefully and maintain logs for debugging purposes.

### 12. HTTP Server Startup
- Upon startup, the server must initialize the HTTP server to serve the SnakeClient.html file to clients.

### 13. Resource Cleanup
- The server must properly release resources and handle cleanup when clients disconnect or when the server shuts down.
