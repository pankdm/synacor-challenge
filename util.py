def inverse(a):
    return a ^ (2**15 - 1)

def mod(v):
    return v % MOD

MEMSIZE = 32768
MAX_VALUE = 32768
MOD = 32768
TRACE = True

def read_memory(v):
    if v < MAX_VALUE:
        return str(v)
    return 'r{}'.format(v - MAX_VALUE)

def is_register(a):
    return MAX_VALUE <= a <= MAX_VALUE + 7

def translate_program(s):
    ops = []
    for i in xrange(0, len(s), 2):
        b1 = ord(s[i])
        b2 = ord(s[i + 1])
        byte = b1 + b2 * 256
        assert byte <= 32775, byte
        ops.append(byte)
    return ops

def load_bytecode():
    f = open('data/challenge.bin', 'rb')
    s = f.read()
    return translate_program(s)
