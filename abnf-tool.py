import pickle
import re

from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf_to_regexp.single_regexp import translate, represent
from greenery import lego

urn_abnf_path = "urn-abnf.txt"

with open(urn_abnf_path, 'r') as f:
    s = f.read()
    rulelist = s.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]


@load_grammar_rules()
class Urn(Rule):
    grammar = rulelist


regex = translate(Urn('namestring'))
urn_re_str = represent(regex).replace('\#', '#').replace('{,', '{0,')
print(urn_re_str)
urn_re = re.compile(urn_re_str)

mrn_abnf_path = "mrn-abnf.txt"

with open(mrn_abnf_path, 'r') as f:
    s = f.read()
    rulelist = s.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]


def parse_regex(regexp):
    return lego.parse(regexp).reduce()


@load_grammar_rules()
class Mrn(Rule):
    grammar = rulelist


# for rule in Mrn.rules():
#     print(f"{rule.name} = {rule.definition}")

regex = translate(Mrn('mrn'))
mrn_re_str = represent(regex).replace('\#', '#').replace('{,', '{0,')
print(mrn_re_str)
# mrn_re = re.compile(mrn_re_str)
#
# start = time.time()

urn_fsm = parse_regex(urn_re_str)
mrn_fsm = parse_regex(mrn_re_str)
# end = time.time()

# duration = end - start
# print(f"Parsing took {duration:.2f} seconds")

with open('urn_lego.bin', 'wb') as f:
    pickle.dump(urn_fsm, f, protocol=pickle.HIGHEST_PROTOCOL)

with open('mrn_lego.bin', 'wb') as f:
    pickle.dump(mrn_fsm, f, protocol=pickle.HIGHEST_PROTOCOL)

#
# if urn_fsm.ispropersuperset(mrn_fsm):
#     print("MRN is a subset of URN")

# test = 'urn:mrn:imo:imo-number:9743368'


# match = re.match(mrn, test)
# print(match)
# if match:
#     print("it matches")
# else:
#     print("it doesn't match")
