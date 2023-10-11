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
import logging
import os
import pickle

from abnf_to_regexp.single_regexp import translate, represent
from greenery import parse
from greenery.fsm import Fsm
from redis import Redis

from mrn import Mrn
from neo4jclient import Neo4JClient
from urn import Urn


def main():
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

    n4j_args = {}
    if args.neo4j_uri:
        n4j_args["host"] = args.neo4j_uri
    if args.neo4j_user:
        n4j_args["username"] = args.neo4j_user
    if args.neo4j_password:
        n4j_args["password"] = args.neo4j_password

    regex = translate(Urn('namestring'))
    urn_re_str = represent(regex).replace('\\#', '#')

    def parse_regex(regexp):
        return parse(regexp).reduce().to_fsm()

    regex = translate(Mrn('mrn'))
    mrn_re_str = represent(regex).replace('\\#', '#')

    log.info("Parsing URN")
    urn_fsm: Fsm = parse_regex(urn_re_str)
    log.info("Parsing MRN")
    mrn_fsm: Fsm = parse_regex(mrn_re_str)

    r = Redis(**redis_args)
    n4j = Neo4JClient(**n4j_args)

    def convert_and_save(fsm: Fsm, name: str, regexp: str, abnf_syntax: str, ns_owner: dict):
        log.info(f"Starting creation of {name}")
        t = {
            "namespace": name,
            "regex": regexp,
            "fsm": fsm,
            "ns_owner": ns_owner
        }
        p = pickle.dumps(t)
        r.set(name, p)
        n4j.create_syntax(abnf_syntax, regexp, name, ns_owner)
        log.info(f"Finished creation of {name}")

    ietf_contact = {
        "name": 'Internet Engineering Task Force',
        "email": 'urn@ietf.org',
        "phone": '',
        "url": 'https://www.ietf.org/',
        "address": '',
        "country": ''
    }
    convert_and_save(urn_fsm, 'urn', urn_re_str, "\r\n".join(Urn.grammar) + "\r\n", ietf_contact)

    iala_contact = {
        "name": 'International Association of Marine Aids to Navigation and Lighthouse Authorities',
        "email": "tm@iala-aism.org",
        "phone": '',
        "url": 'https://www.iala-aism.org/',
        "address": '10 rue des Gaudines\n78100\nSt Germain en Laye',
        "country": 'France'
    }
    convert_and_save(mrn_fsm, 'urn:mrn', mrn_re_str, "\r\n".join(Mrn.grammar) + "\r\n", iala_contact)


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    log = logging.getLogger("Bootstrap")
    main()
