from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf.grammars.rfc3986 import Rule as Uri

from urn import Urn


@load_grammar_rules(
    [
        ('pchar', Uri('pchar')),
        ('rq-components', Urn('rq-components')),
        ('f-component', Urn('f-component')),
        ('alphanum', Urn('alphanum')),
    ]
)
class Mrn(Rule):
    grammar = [
        'mrn = "urn" ":" "mrn" ":" oid ":" oss [rq-components] [ "#" f-component ]',
        'oid = (alphanum) 0*20((alphanum) / "-") (alphanum)',
        'oss = osnid ":" osns',
        'osnid = (alphanum) 0*20((alphanum) / "-") (alphanum)',
        'osns = pchar *(pchar / "/")',
    ]
