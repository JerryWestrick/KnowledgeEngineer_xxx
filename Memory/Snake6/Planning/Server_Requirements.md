# Server Requirements for Snake Online Game

## 1. Python 3 and Async IO
The server must be implemented using Python 3 and utilize the Async IO library to handle asynchronous operations.

## 2. aiohttp Web Server
The server must use the aiohttp library to serve the SnakeClient.html file and handle websocket connections.

## 3. Websocket Support
The server must support websocket connections for real-time communication with clients.

## 4. Game Board Management
The server must maintain a 100x100 2D character array representing the game board, updating it with snake and food positions.

## 5. Game Tick Logic
The server must implement game logic that processes game ticks at a rate of 5 per second, handling snake movements, collisions, and scoring.

## 6. Collision Detection
The server must detect collisions between snakes, food, and the boundaries of the game board.

## 7. Snake Lifecycle Management
The server must handle the lifecycle of snakes, including their creation, movement, death, and scoring.

## 8. Food Management
The server must manage the placement and consumption of food items on the game board.

## 9. Client Management
The server must manage client connections, including joining, disconnection, and reassignment of snake characters.

## 10. Score Tracking
The server must track and update the scores of each client based on game events.

## 11. Client Communication
The server must send updated game status to all connected clients after each tick.

## 12. Error Handling
The server must handle errors gracefully, including client disconnections and invalid game state changes.

## 13. Resource Management
The server must efficiently manage game resources, such as snake characters and food positions, to ensure fair play and performance.

## 14. HTTP Server Startup
The server must start an HTTP server at startup to serve the SnakeClient.html file to clients.

## 15. Client Character Assignment
The server must assign a unique character to each client from a predefined set when they join the game.

## 16. Client Reset
The server must be able to reset a client's snake to a default state upon death or rejoining.

## 17. Client Username Handling
The server must handle client usernames, ensuring they are unique and associated with the correct snake character.

## 18. Client Score Display
The server must maintain and display a list of clients with their characters, usernames, and scores.

## 19. Message Handling
The server must handle different types of messages from clients, such as "Joining", "DirectionChange", and "SnakeDied".

## 20. Security
The server must implement security measures to prevent cheating and unauthorized access to the game server.
