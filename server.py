#!/usr/bin/env python
import asyncio
import websockets


async def hello(ws, path):
    while True:
        name = await ws.recv()
        print(f"< {name}")
        greeting = f"Hello {name}!"
        await ws.send(greeting)
        print(f"> {greeting}")

start_server = websockets.serve(hello, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
