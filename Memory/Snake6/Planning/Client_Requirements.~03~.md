# Client Requirements for Snake Online Game

## 1. Single HTML File
- The client must be contained within a single HTML file, named SnakeClient.html, which includes HTML, CSS, and JavaScript.

## 2. WebSockets Communication
- The client must establish a WebSocket connection to communicate with the server in real-time.

## 3. User Interface
- The client must present a user interface that includes the game board and a status bar for the client list.

## 4. Game Board Display
- The game board must be a 2D 100x100 character array with a default character of " ".
- It should be framed and resizable, with characters that scale with the board size.

## 5. Client List in Status Bar
- The status bar must display the client list at the bottom of the window.
- It should show each client's character, username, and score in the format "{client.char}{client.username}:{client.score} ".

## 6. Username Prompt
- Upon loading, the client must prompt the user to enter a username.

## 7. Joining the Game
- After entering a username, the client must send a "Joining" message to the server via WebSocket.

## 8. Direction Change Handling
- The client must detect arrow key presses and send a "DirectionChange" message with the corresponding direction to the server.

## 9. Handling Snake Death
- When the client receives a "SnakeDied" message, it must display a pop-up dialog to inform the user.

## 10. Game Status Updates
- The client must update the game board and client list based on the "GameStatus" messages received from the server.

## 11. Responsiveness
- The client interface must be responsive and work on various screen sizes and devices.

## 12. Error Handling
- The client must handle errors gracefully, such as lost connections or server errors, and provide feedback to the user.

## 13. Security
- The client should implement basic security measures to ensure safe communication with the server.

## 14. User Experience
- The client must provide a smooth and intuitive gameplay experience, with minimal latency and a clear display of the game state.

## 15. Reconnection Mechanism
- The client should allow users to reconnect to the game in case of disconnection without losing their progress.

## 16. Visual and Audio Feedback
- The client may include visual and audio feedback for game events such as consuming food or snake collisions.

## 17. Accessibility
- The client should be accessible, considering users with disabilities, and follow best practices for web accessibility.

## 18. Customization
- The client may offer customization options for the user, such as different themes or control settings.
