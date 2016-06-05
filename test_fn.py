from util import *

def f2125(r0, r2):
    x = r0 & r2
    x = inverse(x)
    r0 = r0 | r2
    r0 = r0 & x
    return x
