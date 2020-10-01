#!/usr/bin/env python
import asyncio
import websockets


async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        while True:
            name = input("What is you name?")
            await ws.send(name)
            print(f"> {name}")
            greeting = await ws.recv()
            print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())

