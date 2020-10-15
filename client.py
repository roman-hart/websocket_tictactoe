#!/usr/bin/env python
import asyncio
import json
import string
import random
import websockets
from aioconsole import ainput

uri = "ws://localhost:8888"  # server address to connect to
ws = None  # client web socket connection
id_ = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))  # unique token to identify a client


async def consumer():
    try:
        async with websockets.connect(uri) as ws_:
            global ws
            ws = ws_
            await ws.send(json.dumps({'id': id_, 'message': ''}))
            while True:
                msg = await ws.recv()
                if msg != 'ping':
                    print(msg)
                await asyncio.sleep(1)
    except Exception as e:
        print(f'ERROR: {e} \nServer is not available in the moment.')


async def producer():
    while True:
        ans = await ainput()
        if ws:
            try:
                await ws.send(json.dumps({'id': id_, 'message': ans}))
            except Exception as e:
                print(f'ERROR: {e} \nThe message was not sent.')


loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(consumer(), producer()))
loop.run_forever()
