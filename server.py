#  Copyright 2022 International Association of Marine Aids to Navigation and Lighthouse Authorities
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import argparse
import asyncio
import json
import logging
import os
import pickle
import re
import signal

import websockets
from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf.parser import ABNFGrammarRule, ParseError
from abnf_to_regexp.single_regexp import translate, represent
from greenery import fsm, lego
from redis import Redis
from websockets import exceptions

from neo4jclient import Neo4JClient


async def handler(websocket):
    try:
        log.info("Incoming connection")
        message_json = await websocket.recv()
        message = json.loads(message_json)
        function = message["function"]
        if function == "create":
            abnf_syntax = message["abnf"]
            namespace = message["namespace"]
            parent_namespace = message["parent_namespace"]
            namespace_owner = message["namespace_owner"]
            try:
                regex = create_regex_from_abnf(abnf_syntax, namespace, parent_namespace, namespace_owner)
                response = {
                    "code": "OK",
                    "namespace": namespace,
                    "regex": regex
                }
            except (FileNotFoundError, ValueError) as e:
                response = {
                    "code": "ERROR",
                    "message": str(e)
                }
            await websocket.send(json.dumps(response))
            await websocket.close()

        elif function == "get":
            ns = message["namespace"]
            d: dict = pickle.loads(r.get(ns))
            d.pop("fsm")
            await websocket.send(json.dumps(d))
            await websocket.close()
    except exceptions.ConnectionClosedOK:
        log.info("Connected client closed the connection")
    except exceptions.ConnectionClosedError:
        log.error("The connection to the client was terminated with an error")
    except json.JSONDecodeError as e:
        log.exception("The received message could not be decoded as valid JSON", e)
        response = {
            "code": "ERROR",
            "message": str(e)
        }
        await websocket.send(json.dumps(response))


def create_regex_from_abnf(abnf_syntax: str, namespace: str, parent_namespace: str, namespace_owner: dict):
    if not abnf_syntax or not namespace or not parent_namespace or not namespace_owner \
            or not all(key in namespace_owner for key in ('name', 'email', 'phone', 'url', 'address', 'country')):
        raise FileNotFoundError("Mandatory arguments were not provided")

    # Ensure that the syntax uses CRLF as line terminator
    rulelist = abnf_syntax.splitlines()
    abnf_syntax = '\r\n'.join(rulelist) + '\r\n'

    # Check that the provided syntax is actually a valid syntax
    try:
        ABNFGrammarRule("rulelist").parse_all(abnf_syntax)
    except ParseError as e:
        message = "The provided syntax is not a valid ABNF syntax"
        log.exception(message, e)
        raise ValueError(message)

    p = r.get(parent_namespace)
    if not p:
        raise FileNotFoundError(f"A syntax definition was not found for {parent_namespace}")
    extended = pickle.loads(p)
    extended_fsm: fsm.fsm = extended["fsm"]

    if rulelist[-1] == '':
        rulelist = rulelist[:-1]
    rulelist = [rule for rule in rulelist if not re.match(r'^(\s)*;.*$', rule)]

    @load_grammar_rules()
    class NewRule(Rule):
        grammar = rulelist

    new_regex = translate(NewRule)
    new_regex_str = represent(new_regex).replace('\\#', '#')
    new_lego: lego.lego = lego.parse(new_regex_str).reduce()
    new_fsm: fsm.fsm = new_lego.to_fsm().reduce()

    is_subset = new_fsm < extended_fsm
    if not is_subset:
        raise ValueError(f"{namespace} is not a subset of {parent_namespace}")
    new_dict = {
        "namespace": namespace,
        "regex": new_regex_str,
        "fsm": new_fsm
    }
    p = pickle.dumps(new_dict)
    r.set(namespace, p)
    n4j.create_syntax(abnf_syntax, new_regex_str, namespace, namespace_owner)
    return new_regex_str


async def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    log.info("Started server on port 8001")
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()


def initialize_databases():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis_host", help="The host address of the Redis DB")
    parser.add_argument("--redis_port", help="The port of the Redis DB")
    parser.add_argument("--redis_db", help="The DB to use in Redis")
    parser.add_argument("--redis_password", help="The password for Redis")
    parser.add_argument("--neo4j_uri", help="The host URI for the Neo4J DB")
    parser.add_argument("--neo4j_user", help="The username for Neo4J")
    parser.add_argument("--neo4j_password", help="The password for Neo4J")

    args = parser.parse_args()

    redis_args = {}
    if args.redis_host:
        redis_args["host"] = args.redis_host
    if args.redis_port:
        redis_args["port"] = args.redis_port
    if args.redis_db:
        redis_args["db"] = args.redis_db
    if args.redis_password:
        redis_args["password"] = args.redis_password
    redis = Redis(**redis_args)

    n4j_args = {}
    if args.neo4j_uri:
        n4j_args["host"] = args.neo4j_uri
    if args.neo4j_user:
        n4j_args["username"] = args.neo4j_user
    if args.neo4j_password:
        n4j_args["password"] = args.neo4j_password
    neo4j = Neo4JClient(**n4j_args)

    return redis, neo4j


def sig_handler(signum, frame):
    if signum == signal.SIGTERM:
        log.info("Received SIGTERM")
        raise KeyboardInterrupt()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sig_handler)
    r, n4j = initialize_databases()
    log = logging.getLogger("ABNF Server")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Shutting down server")
    finally:
        r.close()
        n4j.close()
