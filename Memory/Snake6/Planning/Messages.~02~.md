# Messages in Snake Online Game

## List of Messages with Senders, Receivers, Descriptions, and Examples

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
- **Description**: Sent by the server to all clients to update the game state.
- **Example**: `{"type": "GameStatus", "game_board": "...", "clients": {...}}`

### 5. WebSocket Disconnect
- **Sender**: Client/Server
- **Receiver**: Server/Client
- **Description**: Implicit message indicating a websocket has disconnected.
- **Example**: *No explicit message, the disconnection event is handled by the server or client.*
