import asyncio
import json
import pickle
import re
from redis import Redis
import websockets

from greenery import fsm, lego

r = Redis()


async def handler(websocket):
    print("Incoming connection")
    message_json = await websocket.recv()
    message = json.loads(message_json)
    if message["function"] == "get":
        ns = message["namespace"]
        syntax = ns
        await websocket.send(syntax)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
