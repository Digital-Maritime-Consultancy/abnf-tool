import asyncio
import json
import websockets

from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf_to_regexp.single_regexp import translate, represent
from redis import Redis

r = Redis()


async def handler(websocket):
    print("Incoming connection")
    message_json = await websocket.recv()
    message = json.loads(message_json)
    function = message["function"]
    if function == "create":
        abnf_syntax = message["abnf"]

    elif function == "get":
        ns = message["namespace"]
        syntax = ns
        await websocket.send(syntax)


def create_regex_from_abnf(abnf_syntax: str):
    rulelist = abnf_syntax.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]

    @load_grammar_rules()
    class NewRule(Rule):
        grammar = rulelist




async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
