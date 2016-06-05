# 6027: f(A, B, C)
# r0 = A
# r1 = B

# r7 = C --> parameter of algo
# 1) A == 0:
#     f(0, B) = B + 1
# 2) A > 0
#     1) B == 0:
#         f(A, 0) = f(A - 1, C)
#     2) B > 0:
#         f(A, B) = f(A - 1, f(A, B - 1))
#
# Observation:
#    f(a, b, c) = X + 1, X
# So we need to compute only first
#
#
# a = 0:
#   f(0, b) = 1 + b
#
# a = 1:
#  b == 0
#    f(1, 0) = f(0, c) = c + 1
#  b > 0
#    f(1, b - 1) = b + c
#    f(0, b + c) = b + c + 1
#  >> f(1, b) = c + 1 + b
#
# a = 2:
#  b == 0
#    f(2, 0) = f(1, c) = c + (1) + c = 2c + 1 = 2c + 1
#  b == 1
#    f(2, 1) = f(1, f(2, 0)) = f(1, 2c + 1) = c + (1) + (2c + 1) = 3c + 2
#    f(2, 2) = f(1, f(2, 1)) = f(1, 3c + 2) = c + (1) + (3c + 2) = 4c + 3
#  >> f(2, b) = 2c + 1 + (c + 1) * b
#
# a = 3:
#  b == 0
#   f(3, 0) = f(2, c) = 2c + 1 + (c + 1) * c = [1, 3, 1]
#  b == 1
#   f(3, 1) = f(2, f(3, 0)) = f(2, [1, 3, 1] = b ) = 2c + 1 + (c + 1) * [1, 3, 1] =
#      = [0, 2, 1] + [1, 3, 1, 0] + [1, 3, 1] = [1, 4, 6, 2]
#   f(3, 2) = f(2, f(3, 1)) = f(2, [2, 6, 5] ) = ...


# Polynomial approach
# Essentially we need to represent f(A, B) = polynomial from B, C and relaclulate
# from previous values
# r7 = C --> parameter of algo
# 1) A == 0:
#     f(0, B) = B + 1
# 2) A > 0
#     1) B == 0:
#         f(A, 0) = f(A - 1, C)
#     2) B > 0:
#         f(A, B) = f(A - 1, f(A, B - 1))





MOD = 32768
MAX_VALUE = 32768
CACHE = {}

def mod(a):
    return ((a % MOD + MOD) % MOD)

F_CACHE = {}


def compute(start, end, dp, c):
    for i in xrange(start, end):
        dp[i] = mod( dp[i - 1] * (c + 1) + 1 + 2 * c )

# return computed hash for this value of register
def compute_c(c):
    dp = [None] * MAX_VALUE
    dp[0] = f_wrapper(2, c, c)

    compute(1, c + 1, dp, c)
    value = dp[c]
    if value <= c:
        return dp[ value ]

    # print 'dp[ {} ] = {}'.format(c, value)
    compute(c + 1, value + 1, dp, c)
    return dp[ value ]

def find_good():
    for c in xrange(1, MAX_VALUE):
        res = compute_c(c)
        print 'Trying ', c, ' --> ', res
        if res == 6:
            print 'Found good: ', c
            return

def prefill(c):
    if c in F_CACHE:
        return
    # here assumes a = 3
    print 'Prefilling cache for', c
    dp = [0] * MAX_VALUE
    dp[0] = f_wrapper(2, c, c)
    for i in xrange(1, MAX_VALUE):
        dp[i] = mod( dp[i - 1] * (c + 1) + 1 + 2 * c )
    F_CACHE[c] = dp

def f4_1(c):
    prefill(c)
    dp = F_CACHE[c]
    return dp[ dp[c] ]

def f_wrapper(a, b, c):
    return f_fast(a, b, c)[0]

def f_fast(a, b, c):
    if a == 0:
        return mod(b + 1), True
    if a == 1:
        return mod(b + c + 1), True
    if a == 2:
        return mod(2 * c + 1 + (c + 1) * b), False
    if a == 3:
        prefill(c)
        return F_CACHE[c][b], False

    assert False, (a, b, c)

def f_6027(a, b, c):
    key = (a, b, c)
    if key in CACHE:
        return CACHE[ key ]

    v0, ok = f_fast(a, b, c)
    if ok and v0 is not None:
        return v0

    f = f_6027
    assert 0 <= a < MOD
    assert 0 <= b < MOD
    assert 0 <= c < MOD

    if a == 0:
        value = mod(b + 1)
    elif b == 0:
        value = f( mod(a - 1), c, c)
    else:
        a1 = f(a, mod(b - 1), c)
        value = f( mod(a - 1), a1, c)

    CACHE[ key ] = value
    print '{} -- > ({} vs {})'.format(
        key, value, v0
    )
    if v0 is not None:
        assert value == v0
    return value

if __name__ == "__main__":
    find_good()
