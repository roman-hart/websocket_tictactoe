#!/usr/bin/env python
import asyncio
import json
import string
import random
import websockets
from aioconsole import ainput


ws = None
uri = "ws://localhost:8888"
d = {'id': ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)), 'message': ''}


async def one():
    print(d['id'])
    async with websockets.connect(uri) as ws_:
        global ws
        ws = ws_
        await ws.send(json.dumps(d))
        while True:
            msg = await ws.recv()
            if msg != 'ping':
                print(msg)
            await asyncio.sleep(1)


async def two():
    while True:
        ans = await ainput()
        d['message'] = ans
        if ws:
            await ws.send(json.dumps(d))


loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(one(), two()))
loop.run_forever()

