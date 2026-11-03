"""Tiny synthetic implementations used to demonstrate a bad test expectation."""
def unsafe(value):
    return bool(value)

def corrected(value):
    return isinstance(value,str) and bool(value.strip())

CASES = (
    ('missing',None,False),
    ('empty','',False),
    ('spaces','   ',False),
    ('tabs-newline','\t\n',False),
    ('valid','Replace a failed keyboard',True),
    ('wrong-type',42,False),
    ('unicode-whitespace','\u2003',False),
)

def acceptance(function):
    results=[{'case':name,'expected':expected,'actual':function(value),'passed':function(value) is expected} for name,value,expected in CASES]
    return {'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'cases':results}
