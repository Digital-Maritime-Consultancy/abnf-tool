import asyncio
import json
import pickle

import websockets
from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf_to_regexp.single_regexp import translate, represent
from greenery import fsm, lego
from redis import Redis

r = Redis()


async def handler(websocket):
    print("Incoming connection")
    message_json = await websocket.recv()
    message = json.loads(message_json)
    function = message["function"]
    if function == "create":
        abnf_syntax = message["abnf"]
        namespace = message["namespace"]
        extends_namespace = message["extends_namespace"]
        try:
            regex = create_regex_from_abnf(abnf_syntax, namespace, extends_namespace)
            response = {
                "namespace": namespace,
                "regex": regex
            }
            await websocket.send(json.dumps(response))
        except (FileNotFoundError, ValueError) as e:
            await websocket.send(str(e))

    elif function == "get":
        ns = message["namespace"]
        d: dict = pickle.loads(r.get(ns))
        d.pop("fsm")
        await websocket.send(json.dumps(d))


def create_regex_from_abnf(abnf_syntax: str, namespace: str, extends_namespace: str):
    if not abnf_syntax or not namespace or not extends_namespace:
        raise FileNotFoundError("Mandatory arguments were not provided")
    p = r.get(extends_namespace)
    if not p:
        raise FileNotFoundError(f"A syntax definition was not found for {extends_namespace}")
    extended = pickle.loads(p)
    extended_fsm: fsm.fsm = extended["fsm"]

    rulelist = abnf_syntax.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]

    @load_grammar_rules()
    class NewRule(Rule):
        grammar = rulelist

    new_regex = translate(NewRule)
    new_regex_str = represent(new_regex).replace('\\#', '#')
    new_lego: lego.lego = lego.parse(new_regex_str).reduce()
    new_fsm: fsm.fsm = new_lego.to_fsm().reduce()

    is_subset = new_fsm < extended_fsm
    if not is_subset:
        raise ValueError(f"{namespace} is not a subset of {extends_namespace}")
    new_dict = {
        "namespace": namespace,
        "regex": new_regex_str,
        "fsm": new_fsm
    }
    p = pickle.dumps(new_dict)
    r.set(namespace, p)
    return new_regex_str


async def main():
    print("Started server on port 8001")
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
