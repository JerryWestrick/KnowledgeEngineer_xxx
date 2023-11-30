# Snake Server

import asyncio
import aiohttp
import websockets


async def handle_client(websocket, path):
    """Handle a client's websocket connection."""
    while True:
        message = await websocket.recv()
        print(message)


async def start_server():
    """Start the Snake server."""
    async with websockets.serve(handle_client, 'localhost', 8765):
        await asyncio.Future()  # Keep the server running


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(start_server())
