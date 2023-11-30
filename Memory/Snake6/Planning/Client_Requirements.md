# Client Requirements for Snake Online Game

## 1. Single HTML File
- The client must be contained within a single HTML file, named SnakeClient.html.
- This file should include HTML, CSS, and JavaScript necessary for the game.

## 2. WebSockets Communication
- The client must use WebSockets to communicate with the server in real-time.
- It should handle messages such as "Joining", "DirectionChange", "SnakeDied", and "GameStatus".

## 3. User Interface
- The client must prompt the user for a username upon starting.
- It should display the game board, a frame around the board, and a status bar for the client list.

## 4. Game Board Display
- The game board must be a 2D 100x100 character array with a default character of " ".
- The board should be resizable, and characters should scale with the board size.

## 5. Client List Display
- The client list must be displayed in a status bar at the bottom of the window.
- It should show each client's character, username, and score in the format "{char}{username}:{score} ".

## 6. User Interaction
- The client must detect arrow key presses to change the direction of the snake.
- It should send the appropriate "DirectionChange" message to the server when an arrow key is pressed.

## 7. Handling Server Messages
- The client must update the game board and client list based on the "GameStatus" message from the server.
- It should display a pop-up dialog when the "SnakeDied" message is received.

## 8. Error Handling
- The client must handle network errors and disconnections gracefully.
- It should attempt to reconnect or inform the user of the issue.

## 9. Visual and Aesthetic Elements
- The client should have a visually appealing design for the game board and status bar.
- It must ensure that the game elements are clearly visible and distinguishable.

## 10. Responsiveness
- The client must be responsive and work on various screen sizes and devices.
- It should maintain functionality and appearance across different browsers.

## 11. Client Initialization
- The client must initialize the connection to the server and handle the joining process.
- It should manage the initial setup, including sending the "Joining" message with the username.

## 12. Client-Side Logic
- The client should implement any necessary logic to display the game state correctly.
- It must not implement game rules or mechanics, as these are handled by the server.

## 13. Accessibility
- The client should be accessible, with considerations for users with disabilities.
- It must follow best practices for web accessibility where applicable.
