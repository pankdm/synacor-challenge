from gdb import *

#USAGE: reload(vault_solver).VaultSolver(x()).solve()

START = 2623
FINISH = 2578
FINISH_VALUE = 30

def is_op(symbol):
    return symbol in ['-', '+', '*']

def apply_op(a, op, b):
    if op == '-':
        return a - b
    if op == '+':
        return a + b
    if op == '*':
        return a * b
    assert False, op


class State:
    def __init__(self, location, path, value, op=None):
        self.path = path
        self.location = location
        self.value = value
        self.op = op

class VaultSolver:
    def __init__(self, gdb):
        locations = gdb.get_vault_info()

        self.map = {}
        for l in locations:
            self.map[ l.pos ] = l

    def print_solution(self, solution):
        now = self.map[START]
        output = [22]
        for move in solution:
            print now.pos, output
            next_pos = now.exits[move]
            now = self.map[next_pos]
            output += [now.symbol]

        print now.pos, output


    def solve(self):
        start_location = self.map[START]
        now = [ State(start_location, [], start_location.symbol) ]
        depth = 15
        for i in xrange(depth):
            next = []
            print 'depth = {}, len = {}'.format(
                i,
                len(now)
            )
            for state in now:
                location = state.location
                # print '(depth = {}): pos = {}, value = {}'.format(
                #     i,
                #     location.pos,
                #     state.value,
                # )
                if location.pos == FINISH:
                    if state.value == FINISH_VALUE:
                        print state.path
                        continue
                    else:
                        continue

                # print location
                for move, next_pos in location.exits.items():
                    if next_pos == START:
                        continue

                    next_location = self.map.get(next_pos, None)
                    if next_location is None:
                        continue
                    if state.op is None:
                        assert is_op(next_location.symbol), next_location.symbol
                        next.append( State(
                            next_location,
                            state.path + [move],
                            state.value,
                            next_location.symbol))
                    else:
                        assert is_op(state.op), state.op
                        assert not is_op(next_location.symbol), next_location.symbol
                        next_value = apply_op(state.value, state.op, next_location.symbol)
                        next.append( State(
                            next_location,
                            state.path + [move],
                            next_value))
            now = next
