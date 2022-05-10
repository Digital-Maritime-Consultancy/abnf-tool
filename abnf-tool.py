from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from greenery import lego
from abnf_to_regexp.single_regexp import *

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
urn_str = represent(regex).replace('\#', '#')
urn = re.compile(urn_str)

mrn_abnf_path = "mrn-abnf.txt"

with open(mrn_abnf_path, 'r') as f:
    s = f.read()
    rulelist = s.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]

@load_grammar_rules()
class Mrn(Rule):
    grammar = rulelist

# for rule in Mrn.rules():
#     print(f"{rule.name} = {rule.definition}")

regex = translate(Mrn('mrn'))
r = represent(regex).replace('\#', '#')
#print(r)
mrn = re.compile(r)

urn_fsm = lego.parse(urn_str).to_fsm()
mrn_fsm = lego.parse(r).to_fsm()

if urn_fsm.ispropersuperset(mrn_fsm):
    print("MRN is a subset of URN")

# test = 'urn:mrn:imo:imo-number:9743368'



# match = re.match(mrn, test)
# print(match)
# if match:
#     print("it matches")
# else:
#     print("it doesn't match")