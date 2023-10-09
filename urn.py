from abnf import Rule
from abnf.grammars.misc import load_grammar_rules
from abnf.grammars.rfc3986 import Rule as Uri


@load_grammar_rules(
    [
        ('pchar', Uri('pchar')),
        ('unreserved', Uri('unreserved')),
        ('pct-encoded', Uri('pct-encoded')),
        ('sub-delims', Uri('sub-delims')),
        ('fragment', Uri('fragment')),
    ]
)
class Urn(Rule):
    grammar = [
        'namestring    = assigned-name [ rq-components ] [ "#" f-component ]',
        'assigned-name = "urn" ":" NID ":" NSS',
        'NID           = (alphanum) 0*30(ldh) (alphanum)',
        'ldh           = alphanum / "-"',
        'NSS           = pchar *(pchar / "/")',
        'rq-components = [ "?+" r-component ] [ "?=" q-component ]',
        'r-component   = pchar *( pchar / "/" / "?" )',
        'q-component   = pchar *( pchar / "/" / "?" )',
        'f-component   = fragment',
        'alphanum      = ALPHA / DIGIT',
    ]
