# Messages in Snake Online Game

## 1. Joining
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client when attempting to join the game, including the username.
- **Example**: `{"type": "Joining", "username": "Player1"}`

## 2. DirectionChange
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to change the direction of their snake.
- **Example**: `{"type": "DirectionChange", "direction": "Up"}`

## 3. GameStatus
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to all clients, containing the full game state including the game board and client list.
- **Example**: `{"type": "GameStatus", "game_board": "[...]", "clients": {"Player1": {"char": "🔴", "score": 150}, "Player2": {"char": "🔵", "score": 423}}}`

## 4. SnakeDied
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to a client when their snake dies.
- **Example**: `{"type": "SnakeDied", "username": "Player1"}`

## 5. WebSocket Disconnect
- **Sender**: Client/Server
- **Receiver**: Server/Client
- **Description**: Implicit message indicating that a websocket connection has been closed.
- **Example**: N/A (WebSocket protocol level message)
