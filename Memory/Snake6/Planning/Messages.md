# Messages in Snake Online Game

## 1. Joining
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to join the game with a username.
- **Example**: `{"type": "Joining", "username": "Player1"}`

## 2. DirectionChange
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to change the direction of their snake.
- **Example**: `{"type": "DirectionChange", "direction": "Up"}`

## 3. SnakeDied
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to the client when their snake dies.
- **Example**: `{"type": "SnakeDied", "username": "Player1"}`

## 4. GameStatus
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to all clients after each tick to update the game state.
- **Example**: `{"type": "GameStatus", "game_board": "updated_board", "clients": {"Player1": {"char": "🔴", "score": 150}, "Player2": {"char": "🔵", "score": 423}}}`

## 5. ClientDisconnected
- **Sender**: Server
- **Receiver**: Server (internal)
- **Description**: Used by the server to handle a client's disconnection.
- **Example**: `{"type": "ClientDisconnected", "username": "Player1"}`

## 6. ResetClient
- **Sender**: Server
- **Receiver**: Server (internal)
- **Description**: Used by the server to reset a client's game state after death or joining.
- **Example**: `{"type": "ResetClient", "username": "Player1"}`

## 7. AddFood
- **Sender**: Server
- **Receiver**: Server (internal)
- **Description**: Used by the server to add a new food item to the game board.
- **Example**: `{"type": "AddFood", "position": (x, y)}`

## 8. UpdateScore
- **Sender**: Server
- **Receiver**: Server (internal)
- **Description**: Used by the server to update a client's score.
- **Example**: `{"type": "UpdateScore", "username": "Player1", "score": 100}`

## 9. EraseSnake
- **Sender**: Server
- **Receiver**: Server (internal)
- **Description**: Used by the server to remove a snake from the game board.
- **Example**: `{"type": "EraseSnake", "username": "Player1"}`

## 10. HTTPRequest
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to request the SnakeClient.html file.
- **Example**: `GET /SnakeClient.html HTTP/1.1`

Note: Messages 5 to 9 are internal server messages and are not sent over the network but are used for server logic and state management.
