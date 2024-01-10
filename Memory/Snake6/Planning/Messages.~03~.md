# Messages in Snake Online Game

## 1. Joining
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client when attempting to join the game, containing the username.
- **Example**: `{"type": "Joining", "username": "Player1"}`

## 2. DirectionChange
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to change the direction of their snake.
- **Example**: `{"type": "DirectionChange", "direction": "Up"}`

## 3. GameStatus
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to all clients, containing the current state of the game.
- **Example**: 
  ```
  {
    "type": "GameStatus",
    "game_board": "updated game board string",
    "clients": {
      "websocket1": {"name": "Jerry", "char": "🔴", "snake": [(5, 3), (5, 4), (6, 4)], "score": 130, "direction": "Up"},
      "websocket2": {"name": "Tom", "char": "🔵", "snake": [(6, 12), (6, 13), (6, 14)], "score": 30, "direction": "Left"}
    }
  }
  ```

## 4. SnakeDied
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to a client when their snake dies.
- **Example**: `{"type": "SnakeDied", "username": "Player1"}`

## 5. WebSocket Disconnect
- **Sender**: Client
- **Receiver**: Server
- **Description**: Implicit message sent when a client's WebSocket connection is closed.
- **Example**: *No explicit message, the server detects the closed connection.*
