# Messages in Snake Online Game

## List of Messages with Senders, Receivers, Description, and Examples

### 1. Joining
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to join the game with a username.
- **Example**: `{"type": "Joining", "username": "Player1"}`

### 2. DirectionChange
- **Sender**: Client
- **Receiver**: Server
- **Description**: Sent by the client to change the direction of their snake.
- **Example**: `{"type": "DirectionChange", "direction": "Up"}`

### 3. SnakeDied
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to the client when their snake dies.
- **Example**: `{"type": "SnakeDied", "username": "Player1"}`

### 4. GameStatus
- **Sender**: Server
- **Receiver**: Client
- **Description**: Sent by the server to all clients with the current state of the game.
- **Example**: `{"type": "GameStatus", "game_board": "...", "clients": {"Player1": {"char": "🔴", "snake": [...], "score": 127, "direction": "Up"}, "Player2": {"char": "🔵", "snake": [...], "score": 27, "direction": "Left"}}}`

### 5. ClientDisconnected
- **Sender**: Server
- **Receiver**: Server
- **Description**: Internal message for the server when a client disconnects.
- **Example**: `{"type": "ClientDisconnected", "websocket": websocket1}`

These messages facilitate real-time communication between clients and the server, ensuring a smooth and interactive gaming experience.