from util import *

SPEC = [
    ('halt', '0'),
    ('set', '1 a b'),
    ('push', '2 a'),
    ('pop', '3 a'),
    ('eq', '4 a b c'),
    ('gt', '5 a b c'),
    ('jmp', '6 a'),
    ('jt', '7 a b'),
    ('jf', '8 a b'),
    ('add', '9 a b c'),
    ('mult', '10 a b c'),
    ('mod', '11 a b c'),
    ('and', '12 a b c'),
    ('or', '13 a b c'),
    ('not', '14 a b'),
    ('rmem', '15 a b'),
    ('wmem', '16 a b'),
    ('call', '17 a'),
    ('ret', '18'),
    ('out', '19 a'),
    ('in', '20 a'),
    ('noop', '21'),
]

class OpSpec:
    def __init__(self, name=None, spec=None):
        if name is not None:
            self.name = name
            ss = spec.split(' ')
            self.opcode = int(ss[0])
            self.arity = len(ss) - 1
            self.args = ", ".join(ss[1:])

    def size(self):
        return self.arity + 1

    @staticmethod
    def unknown():
        op = OpSpec()
        op.name = 'unknown'
        op.arity = 0
        op.args = ''
        return op


CODES = {}
for name, s in SPEC:
    op = OpSpec(name, s)
    CODES[op.opcode] = op


OPNAME_TO_CODE = {}
for op in CODES.values():
    OPNAME_TO_CODE[op.name] = op.opcode

def to_opcode(s):
    if s in OPNAME_TO_CODE:
        return OPNAME_TO_CODE[s]
    if s.startswith('r'):
        return int(s[1:]) + MAX_VALUE
    return int(s)
