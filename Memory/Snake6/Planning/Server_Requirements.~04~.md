# Server Requirements for Snake Online Game

## 1. Python 3 and Async IO
- The server must be implemented using Python 3.
- It should utilize asynchronous I/O operations to handle multiple client connections efficiently.

## 2. aiohttp Web Server
- The server should use the aiohttp library to serve the SnakeClient.html file.
- It must handle HTTP requests and serve static files required by the client.

## 3. WebSockets Support
- The server must support WebSocket connections for real-time communication with clients.
- It should manage multiple WebSocket connections concurrently.

## 4. Game Board Management
- The server must maintain a 100x100 2D character array representing the game board.
- It should update the game board with snake and food positions and check for collisions.

## 5. Game Tick Logic
- The server must implement game logic that progresses in ticks, with 5 ticks per second.
- Each tick involves moving snakes, checking for collisions, updating scores, and sending the updated game state to clients.

## 6. Snake Movement and Collision Detection
- The server must handle snake movement based on client directions.
- It should detect collisions with the game board boundaries, other snakes, or food.

## 7. Food Mechanics
- The server must manage the placement and consumption of food items on the game board.
- It should randomly place new food items when consumed by a snake.

## 8. Scoring System
- The server must keep track of each client's score, increasing it when a snake consumes food or moves without dying.

## 9. Client Management
- The server must handle client connections, disconnections, and reconnections.
- It should manage client-specific data such as snake characters, scores, and usernames.

## 10. Client Character Assignment
- The server must assign a unique character to each client from a predefined set of characters.
- It should handle the return of characters to the pool when clients disconnect.

## 11. Client Death and Respawn
- The server must handle the death of a client's snake and respawn the snake at a new location.
- It should reset the client's score and direction upon respawning.

## 12. Joining and Leaving the Game
- The server must process "Joining" messages from new clients and assign them a character and initial position.
- It should handle the removal of clients from the game state when they disconnect.

## 13. HTTP Server Startup
- The server must start an HTTP server at launch to serve the SnakeClient.html file to clients.

## 14. Game State Broadcasting
- The server must broadcast the current game state to all connected clients after each tick.

## 15. Error Handling
- The server must handle errors gracefully, including client disconnections and invalid messages.

## 16. Security
- The server should implement basic security measures to prevent unauthorized access and ensure safe communication.

## 17. Logging
- The server must implement logging to record game events, client actions, and potential errors for debugging purposes.

## 18. Configuration
- The server should be configurable, allowing for adjustments to game parameters such as board size and tick rate.
