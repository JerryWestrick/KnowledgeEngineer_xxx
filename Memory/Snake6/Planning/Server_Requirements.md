# Server Requirements for Snake Online Game

## 1. Python 3 and Async IO
- The server must be implemented using Python 3.
- It should utilize asynchronous I/O operations to handle multiple clients simultaneously.

## 2. aiohttp Web Server
- The server should use the aiohttp library to serve the SnakeClient.html file.
- It must be capable of handling HTTP requests and serving static files.

## 3. WebSockets Support
- The server must support WebSockets for real-time communication with clients.
- It should handle incoming connections, messages, and disconnections.

## 4. Game Board Management
- The server must maintain a 100x100 2D character array representing the game board.
- It should update the game board with snake and food positions and check for collisions.

## 5. Game Ticks
- The server must implement game ticks, with 5 ticks per second.
- Each tick involves moving snakes, checking for collisions, updating scores, and managing food items.

## 6. Snake Movement and Collision Detection
- The server must calculate new snake head positions based on their direction.
- It should detect collisions with the game board boundaries, other snakes, or food.

## 7. Score and Food Management
- The server must update scores when snakes eat food.
- It should manage the placement of new food items on the game board.

## 8. Client Management
- The server must handle client connections, including assigning snake characters and resetting clients.
- It should manage the list of available snake characters and client scores.

## 9. Handling Client Messages
- The server must process "Joining", "DirectionChange", and other relevant messages from clients.
- It should respond appropriately, including resetting clients or changing snake directions.

## 10. Client Disconnection
- The server must handle client disconnections gracefully.
- It should return the snake character to the pool and remove the client's snake from the game board.

## 11. Sending Game Status
- The server must send the current game status to all connected clients after each tick.
- It should include the updated game board and client list.

## 12. HTTP Server Startup
- The server must start an HTTP server at startup to serve the SnakeClient.html file.
- It should be accessible to clients for downloading and playing the game.

## 13. Error Handling
- The server must implement robust error handling to manage exceptions and unexpected behavior.
- It should ensure the game continues to run smoothly for all clients.
