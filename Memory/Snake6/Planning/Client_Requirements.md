# Client Requirements for Snake Online Game

## Detailed Description of Each Requirement

### 1. Single HTML File
- The client must be contained within a single HTML file, named SnakeClient.html, which includes HTML, CSS, and JavaScript.

### 2. WebSocket Communication
- The client must establish a WebSocket connection to communicate with the server in real-time.
- It should handle messages such as 'Joining', 'DirectionChange', 'SnakeDied', and 'GameStatus'.

### 3. User Interface
- The client should prompt the user for a username upon starting.
- It must display the game board with a frame and ensure that it is resizable.
- The characters on the game board should resize with the board.
- A status bar at the bottom of the window should display the client list with characters, usernames, and scores.

### 4. User Input
- The client must detect arrow key presses to change the direction of the snake.
- It should send the 'DirectionChange' message with the new direction to the server.

### 5. Game Status Updates
- The client must update the game board and client list based on the 'GameStatus' messages received from the server.

### 6. Handling Game Events
- The client should display a pop-up dialog when the 'SnakeDied' message is received.

### 7. Error Handling
- The client must handle errors gracefully, such as server disconnection or full game.

### 8. Responsiveness
- The client interface should be responsive and work across different screen sizes and devices.

These requirements ensure that the client can interact with the server, display the game state, and provide a user-friendly experience.