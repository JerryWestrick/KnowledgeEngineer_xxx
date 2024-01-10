Messages

| Message | Sender | Receiver | Description | Example |
|---------|--------|----------|-------------|---------|
| Joining | Client | Server | Sent by the client when joining the game. Includes the username. | {"message": "Joining", "username": "Alice"} |
| DirectionChange | Client | Server | Sent by the client when the arrow keys are pressed to change the snake's direction. Includes the new direction. | {"message": "DirectionChange", "direction": "Up"} |
| SnakeDied | Server | Client | Sent by the server when a snake dies. Notifies the client that their snake has died. | {"message": "SnakeDied"} |
| GameStatus | Server | Client | Sent by the server to update the client with the current game status. Includes the game board and client list. | {"message": "GameStatus", "game_board": [...], "client_list": [...]} |
