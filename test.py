import pickle
import tempfile
from neo4jclient import Neo4JClient
from redis import Redis

from greenery import fsm, lego

n4j = Neo4JClient()
r = Redis()
result = n4j.find_namespace("urn:mrn:mcp")
print(result)
d = pickle.loads(r.get("urn:mrn:mcp"))
syntax = "mcp-mrn = \"urn:mrn:mcp:\" mcp-type \":\" ipid \":\" ipss\r\nmcp-type = \"device\" / \"org\" / \"user\" / \"vessel\" / \"service\"\r\nipid = alphanum *20(alphanum / \"-\") alphanum\r\nipss = pchar *(pchar / \"/\")\r\nalphanum = ALPHA / DIGIT\r\npchar = unreserved / pct-encoded / sub-delims / \":\" / \"@\"\r\nunreserved = ALPHA / DIGIT / \"-\" / \".\" / \"_\" / \"~\"\r\npct-encoded = \"%\" HEXDIG HEXDIG\r\nsub-delims = \"!\" / \"$\" / \"&\" / \"'\" / \"(\" / \")\" / \"*\" / \"+\" / \",\" / \";\" / \"=\"\r\n"
result = n4j.create_syntax(syntax, d["regex"], "urn:mrn:mcp")
n4j.close()

# r1 = "[A-Za-z0-9]{0,4}"
# r2 = "[A-Za-z0-9]{0,3}"
#
# l1: lego.lego = lego.parse(r1)
# l2: lego.lego = lego.parse(r2)
#
# f1: fsm.fsm = l1.to_fsm()
# f2: fsm.fsm = l2.to_fsm()
#
# tempdir = tempfile.gettempdir()
#
# if f2 < f1:
#     print("r2 is a proper subset of r1")
# else:
#     print("r2 is NOT is proper subset of r1")
#
# with open(f"{tempdir}/f1.bin", "wb") as f:
#     pickle.dump(f1, f)
#
# with open(f"{tempdir}/f2.bin", "wb") as f:
#     pickle.dump(f2, f)
#
# with open(f"{tempdir}/f1.bin", "rb") as f:
#     f1_unpickled: fsm.fsm = pickle.load(f)
#
# with open(f"{tempdir}/f2.bin", "rb") as f:
#     f2_unpickled: fsm.fsm = pickle.load(f)
#
# if f2_unpickled < f1_unpickled:
#     print("r2 is a proper subset of r1")
# else:
#     print("r2 is NOT is proper subset of r1")


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
