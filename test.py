import pickle

from greenery import fsm, lego

r1 = "[A-Za-z0-9]{0,4}"
r2 = "[A-Za-z0-9]{0,3}"

l1: lego.lego = lego.parse(r1)
l2: lego.lego = lego.parse(r2)

f1: fsm.fsm = l1.to_fsm()
f2: fsm.fsm = l2.to_fsm()

if f2 < f1:
    print("r2 is a proper subset of r1")
else:
    print("r2 is NOT is proper subset of r1")

with open("/tmp/f1.bin", "wb") as f:
    pickle.dump(f1, f)

with open("/tmp/f2.bin", "wb") as f:
    pickle.dump(f2, f)

with open("/tmp/f1.bin", "rb") as f:
    f1_unpickled: fsm.fsm = pickle.load(f)

with open("/tmp/f2.bin", "rb") as f:
    f2_unpickled: fsm.fsm = pickle.load(f)

if f2_unpickled < f1_unpickled:
    print("r2 is a proper subset of r1")
else:
    print("r2 is NOT is proper subset of r1")


# with open('urn_fsm.bin', 'rb') as f:
#     urn_fsm: fsm.fsm = pickle.load(f)
#
# with open('mrn_fsm.bin', 'rb') as f:
#     mrn_fsm: fsm.fsm = pickle.load(f)
#
# if mrn_fsm < urn_fsm:
#     print("This is good")
# else:
#     print("This is bad")
