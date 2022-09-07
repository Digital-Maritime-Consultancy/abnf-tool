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

import pickle
import re

from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf.parser import ABNFGrammarRule, ParseError
from abnf_to_regexp.single_regexp import translate, represent
from greenery import lego, fsm
from neo4jclient import Neo4JClient
from redis import Redis

urn_abnf_path = "urn-abnf.txt"

with open(urn_abnf_path, 'rt') as f:
    s = f.read().splitlines()
    urn_abnf = '\r\n'.join(s) + '\r\n'
    try:
        print("Checking if URN ABNF is valid")
        ABNFGrammarRule('rulelist').parse_all(urn_abnf)
    except ParseError as e:
        print("URN ABNF could not be parsed", e)
        exit(1)
    rulelist = urn_abnf.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]


@load_grammar_rules()
class Urn(Rule):
    grammar = rulelist


regex = translate(Urn('namestring'))
urn_re_str = represent(regex).replace('\#', '#')
print(urn_re_str)
urn_re = re.compile(urn_re_str)

mrn_abnf_path = "mrn-abnf.txt"

with open(mrn_abnf_path, 'rt') as f:
    s = f.read().splitlines()
    mrn_abnf = '\r\n'.join(s) + '\r\n'
    try:
        print("Checking if MRN ABNF is valid")
        ABNFGrammarRule('rulelist').parse_all(mrn_abnf)
    except ParseError as e:
        print("MRN ABNF could not be parsed", e)
        exit(1)
    rulelist = mrn_abnf.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]


def parse_regex(regexp):
    return lego.parse(regexp).reduce()


@load_grammar_rules()
class Mrn(Rule):
    grammar = rulelist


regex = translate(Mrn('mrn'))
mrn_re_str = represent(regex).replace('\#', '#')
print(mrn_re_str)

urn_lego: lego.lego = parse_regex(urn_re_str)
mrn_lego: lego.lego = parse_regex(mrn_re_str)

r = Redis()
n4j = Neo4JClient()


def convert_and_save(lego_piece: lego.lego, name: str, regexp: str, abnf_syntax: str, ns_owner: dict):
    print(f"Starting creation of {name}")
    _fsm: fsm.fsm = lego_piece.to_fsm().reduce()
    t = {
        "namespace": name,
        "regex": regexp,
        "fsm": _fsm,
        "ns_owner": ns_owner
    }
    p = pickle.dumps(t)
    r.set(name, p)
    n4j.create_syntax(abnf_syntax, regexp, name, ns_owner)
    print(f"Finished {name}")


ietf_contact = {
    "name": 'Internet Engineering Task Force',
    "email": 'urn@ietf.org',
    "phone": '',
    "url": 'https://www.ietf.org/',
    "address": '',
    "country": ''
}
convert_and_save(urn_lego, 'urn', urn_re_str, urn_abnf, ietf_contact)
iala_contact = {
    "name": 'International Association of Marine Aids to Navigation and Lighthouse Authorities',
    "email": "tm@iala-aism.org",
    "phone": '',
    "url": 'https://www.iala-aism.org/',
    "address": '10 rue des Gaudines\n78100\nSt Germain en Laye',
    "country": 'France'
}
convert_and_save(mrn_lego, 'urn:mrn', mrn_re_str, mrn_abnf, iala_contact)
