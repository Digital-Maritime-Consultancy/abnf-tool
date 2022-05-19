import pickle
import re
from multiprocessing import Process

from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf_to_regexp.single_regexp import translate, represent
from greenery import lego, fsm
from redis import Redis

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
urn_re_str = represent(regex).replace('\#', '#')
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
mrn_re_str = represent(regex).replace('\#', '#')
print(mrn_re_str)
# mrn_re = re.compile(mrn_re_str)
#
# start = time.time()

urn_lego: lego.lego = parse_regex(urn_re_str)
mrn_lego: lego.lego = parse_regex(mrn_re_str)

# end = time.time()

# duration = end - start
# print(f"Parsing took {duration:.2f} seconds")

with open('urn_lego.bin', 'wb') as f:
    pickle.dump(urn_lego, f)

with open('mrn_lego.bin', 'wb') as f:
    pickle.dump(mrn_lego, f)


r = Redis()


def convert_and_save(lego_piece: lego.lego, path: str, name: str, regexp: str):
    print(f"Starting creation of {name}")
    _fsm: fsm.fsm = lego_piece.to_fsm().reduce()
    with open(path, 'wb') as file:
        pickle.dump(_fsm, file)
    t = {
        "namespace": name,
        "regex": regexp,
        "fsm": _fsm
    }
    p = pickle.dumps(t)
    r.set(name, p)
    print(f"Finished {name}")


# with open(path, 'rb') as file:
    #     fsm_loaded = pickle.load(file)
    # if _fsm == fsm_loaded:
    #     print("FSM is the same after pickling", path)
    # else:
    #     print("FSM is NOT the same after pickling", path)


convert_and_save(urn_lego, 'urn_fsm.bin', 'urn', urn_re_str)
convert_and_save(mrn_lego, 'mrn_fsm.bin', 'urn:mrn', mrn_re_str)
# p1 = Process(target=convert_and_save, args=(urn_lego, 'urn_fsm.bin', 'urn',))
# p2 = Process(target=convert_and_save, args=(mrn_lego, 'mrn_fsm.bin', 'urn:mrn',))
# p1.start()
# p2.start()
# p1.join()
# p2.join()

# if urn_fsm.ispropersuperset(mrn_fsm):
#     print("MRN is a subset of URN")

# test = 'urn:mrn:imo:imo-number:9743368'


# match = re.match(mrn, test)
# print(match)
# if match:
#     print("it matches")
# else:
#     print("it doesn't match")
