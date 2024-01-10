Client Requirements

1. Architecture

The client part of the multi-user 'Snake' online game will be implemented as a single file called SnakeClient.html. It will use HTML, CSS, JavaScript, and websockets.

2. Game Board

The game board will be a resizable 2D grid with a size of 100x100. It will display a frame and the characters representing the snakes and foods. The characters displayed on the board should be resized along with the board.

3. Client List

The client list will be displayed in a status bar at the bottom of the window. It will show the character, username, and score for each client in the game.

4. Client Initialization

The client will prompt the user for a username and connect to the server via a websocket. It will send a 'Joining' message to the server, including the username.

5. Arrow Key Detection

The client will detect arrow key presses and send a 'DirectionChange' message to the server with the corresponding direction (Up, Down, Left, or Right).

6. Snake Died

When the client receives a 'SnakeDied' message from the server, it should display a pop-up dialog to notify the user.

7. Game Status

When the client receives a 'GameStatus' message from the server, it should update the game board and client list with the values from the message.
