import pickle

from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from greenery import fsm, lego
from abnf_to_regexp.single_regexp import translate, represent


with open('mrn_lego.bin', 'rb') as f:
    mrn_lego: lego.lego = pickle.load(f)


def lego_to_fsm(_lego: lego.lego):
    return _lego.to_fsm()


mrn_fsm: fsm.fsm = lego_to_fsm(mrn_lego)
print("Loaded MRN FSM")

with open('mcp-mrn-abnf.txt', 'r') as f:
    s = f.read()
    rulelist = s.splitlines()
    if rulelist[-1] == '':
        rulelist = rulelist[:-1]


@load_grammar_rules()
class McpMrn(Rule):
    grammar = rulelist


mcp_mrn = translate(McpMrn)
mcp_mrn_str = represent(mcp_mrn).replace('{,', '{0,')
print(mcp_mrn_str)

mcp_mrn_lego: lego.lego = lego.parse(mcp_mrn_str)
mcp_mrn_fsm: fsm.fsm = mcp_mrn_lego.to_fsm()
print("Loaded MCP MRN FSM")

if mcp_mrn_fsm.ispropersubset(mrn_fsm):
    print("MCP MRN is a proper subset of MRN")
else:
    print("MCP MRN is NOT a proper subset of MRN")
