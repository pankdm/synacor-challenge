from util import *
from ops import *

import re

from itertools import permutations

def unhash(code, seed):
   # r1: seed
   # 2125| ;;;
   # 2129| and r2 r0 r1
   # 2133| not r2 r2
   # 2136| or r0 r0 r1
   # 2140| and r0 r0 r2
   r2 = code & seed
   r2 = inverse(r2)
   code = code | seed
   code = code & r2
   return code


# movement solutions
def take_lantern_and_go_to_ladder():
    s = ['doorway', 'north', 'north', 'bridge', 'continue', 'down', 'east',
    'take empty lantern', 'west', 'west', 'passage', 'ladder']
    return s

def go_to_door_from_ladder():
    # assume starts in ladder
    s = ['ladder'] # go back
    s += ['darkness', 'continue', 'west', 'west',
    'west', 'west', 'north', 'north']
    return s

def take_can_in_maze():
    # assume starts in ladder
    s = ['west', 'south', 'north', 'take can', 'west']
    return s

def light_lantern():
    s = ['use can', 'use lantern']
    return s

def gather_coins():
    # assume start at door
    s = ['south', 'take red coin', 'north', 'east', 'take concave coin',
    'down', 'take corroded coin', 'up', 'west', 'west', 'take blue coin',
    'up', 'take shiny coin', 'down', 'east']
    return s

def solve_door():
    #  9 + 2 * 5^2 + 7^3 - 3 = 399
    s = ['use blue coin', 'use red coin', 'use shiny coin',
    'use concave coin', 'use corroded coin']
    return s

def take_and_use_teleport():
    # assumes start at door
    s = ['north', 'take teleporter', 'use teleporter']
    return s

def go_to_antechamber():
    # assume starts at island
    s = ['west', 'north', 'east', 'north', 'north', 'north', 'north',
    'north', 'north', 'north', 'north']
    return s

def solution_to_vault():
    s = ['north', 'east', 'east', 'north', 'west', 'south', 'east', 'east',
    'west', 'north', 'north', 'east']
    return s

def solve_vault():
    return ['take orb'] + solution_to_vault()

def enter_vault_and_get_mirror():
    return ['vault', 'take mirror', 'use mirror']

class FindResult:
    def __init__(self, pos, context):
        self.pos = pos
        self.context = context
        self.info = ' (??)'


class LocationInfo:
    def __init__(self, pos, name, desc, exits):
        self.pos = pos
        self.name = name
        self.desc = desc

        self.exits = {}
        for move, next_pos in exits:
            self.exits[move] = next_pos

        self.symbol = None
        # print 'Creating info for ', repr(self)
        ss = self.symbol_impl()
        if ss in ['+', '-', '*']:
            self.symbol = ss
        else:
            self.symbol = int(ss)

    def __repr__(self):
        return 'LocationInfo({}):\nname = {}\ndesc = {}\nsymbol = {}\nexits = {}'.format(
            self.pos,
            self.name,
            self.desc,
            self.symbol,
            self.exits
        )

    def symbol_impl(self):
        re1 = "the number '(.*?)'"
        re2 = "depicting a '(.*)' symbol"
        m1 = re.search(re1, self.desc)
        m2 = re.search(re2, self.desc)
        if m1 is not None:
            return m1.group(1)
        elif m2 is not None:
            return m2.group(1)
        else:
            return None

# limit on textual output of memory fields
LOC_LIMIT = 300
ITEM_LIMIT = 100
PRINT_LIMIT = 300


class GDB:
    def __init__(self, vm):
        self.vm = vm

        self.annotations = [''] * MEMSIZE
        self.funcs = [None] * MEMSIZE

    def go(self):
        self.vm.return_on_input = False
        self.vm.run()

    def find_begin(self, pos):
        F_LIMIT = 1000
        start = max(0, pos - F_LIMIT)

        begin = pos
        for i in xrange(start, pos):
            # 'ret'
            if self.vm.memory[i] == 18:
                begin = i
        return begin

    def analyze(self):
        good, bad = self.filter_by_pattern_1458()
        for find_result in good:
            start = self.find_begin(find_result.pos)
            self.annotations[find_result.pos] = find_result.info
            for i in xrange(start, find_result.pos + 1):
                # print 'Added ', find_result.info, 'at ', i
                self.funcs[i] = find_result.info

        # CODE_END = 6067
        # now = 0
        # while now < CODE_END:
        #     op = self.vm.read_op(now)
        #     if op.name == 'call':
        #         addr = self.vm[now + 1]
        #         if addr < CODE_END and self.funcs[addr] != '':

    def read_raw_string(self, r0, limit=None):
        m = self.vm.memory
        output = ''
        length = m[r0]
        if limit is not None:
            length = min(limit, length)

        for i in xrange(length):
            code = m[r0 + 1 + i]
            if code <= 128:
                output += chr(code)
            else:
                output += '?'
        return output

    def read_string(self, r0, r1, r2):
        hashing = False
        if r1 == 1531:
            hashing = True

        m = self.vm.memory
        output = ''

        length = m[r0]
        for i in xrange(length):
            code = m[r0 + 1 + i]
            if hashing:
                output += chr(unhash(code, r2))
            else:
                output += chr(code)
        return output

    def try_read_string(self, offset, limit=1000):
        output = ''
        m = self.vm.memory
        for i in xrange(limit):
            if offset + i >= len(m):
                break
            code = m[offset + i]
            if 32 <= code <= 128:
                output += chr(code)
            elif code == 10:
                output += '\\n'
            else:
                output += 'chr({}) '.format(code)
        return output

    def find_calls(self, addr):
        result = []
        m = self.vm.memory
        ln = len(m)
        for i in xrange(ln):
            if i + 1 < ln:
                a, b = m[i: i + 2]
                # call addr
                if (a, b) == (17, addr):
                    result.append(i)
        return result



    def try_match_pattern(self, pos, pattern, values):
        vm = self.vm
        m = vm.memory
        ok = True
        start = pos - len(pattern)
        for i in xrange(len(pattern)):
            if pattern[i].startswith('>'):
                if m[start + i] >= MAX_VALUE:
                    ok = False
                    break

                values[ pattern[i][1:] ] =  m[start + i]
            elif m[start + i] != to_opcode(pattern[i]):
                ok = False
                break
        return ok

    def next(self):
        self.vm.execute_one_op(ignore_break=True)


    def up(self):
        self.depth = 0
        self.vm.stop_on_return = True
        self.vm.run()
        self.vm.stop_on_return = False

    def try_match_1518(self, pos):
        pattern = [
            'set', 'r0', '>A',
        ]
        values = {}
        ok = self.try_match_pattern(pos, pattern, values)
        if ok:
            context = {}
            context['r0'] = values['A']
            find_result = FindResult(pos, context)

            c = context
            s = self.read_raw_string(c['r0'])
            find_result.info = '  // print "{}"'.format(
                s[:PRINT_LIMIT].replace('\n', '\\n')
            )
            return find_result
        return None


    def try_match_1458_r1_1531(self, pos):
        pattern = [
            'set', 'r0', '>A',
            'set', 'r1', '>B',
            'add', 'r2', '>C', '>D',
        ]
        values = {}
        ok = self.try_match_pattern(pos, pattern, values)
        if ok:
            context = {}
            context['r0'] = values['A']
            context['r1'] = values['B']
            context['r2'] = values['C'] + values['D']
            find_result = FindResult(pos, context)

            c = context
            s = self.read_string(c['r0'], c['r1'], c['r2'])
            find_result.info = '  // print "{}"'.format(
                s[:100].replace('\n', '\\n')
            )
            return find_result
        return None


    def filter_by_pattern_1458(self):
        pts = self.find_calls(1458)

        results = []
        not_matched = []

        for pos in pts:
            values = {}
            find_result = self.try_match_1458_r1_1531(pos)
            if find_result is not None:
                results.append(find_result)
            else:
                not_matched.append(pos)
        return results, not_matched

    def run_seq(self, s, show_output=False):
        self.vm.buffer += '\n'.join(s) + '\n'

        if show_output:
            self.vm.run()
        else:
            self.vm.disable_output = True
            self.vm.run()
            self.vm.disable_output = False


    def solution(self):
        def do(f, show_output=False):
            print 'Executing', f.__name__
            s = f()
            self.run_seq(s, show_output)

        do( take_lantern_and_go_to_ladder )
        do( take_can_in_maze )
        do( light_lantern )
        do( go_to_door_from_ladder )
        do( gather_coins )
        do( solve_door )
        do( take_and_use_teleport )

        # set right amount of energy and teleport again
        self.vm.r[7] = 25734
        do( lambda : ['use teleporter'] )

        do( go_to_antechamber )
        do( solve_vault, show_output=True)
        do( enter_vault_and_get_mirror, show_output=True)


    def get_all_items(self):
        pos = 2668
        while pos <= 2728:
            self.vm.memory[pos + 2] = 0
            pos += 4

    def read_location_desc(self, offset):
        code = self.vm.memory[offset]
        max_length = self.vm.memory[code]
        length = min(max_length, LOC_LIMIT)
        s = self.try_read_string(code + 1, limit=length)
        return s

    def get_vault_info(self):
        locations = []
        for pos in xrange(2563, 2643, 5):
            locations.append( self.get_location_info(pos) )
        return locations

    def get_location_info(self, pos):
        name = self.read_location_desc(pos)
        desc = self.read_location_desc(pos + 1)
        exits = []

        exits_str_code = self.vm.memory[pos + 2] # 26900 <-- code
        exits_pos_code = self.vm.memory[pos + 3]
        num_exits = self.vm.memory[exits_str_code]

        for i in xrange(num_exits):
            exit_str_addr = self.vm.memory[exits_str_code + 1 + i]
            exit_str = self.read_raw_string(exit_str_addr, limit=20)

            exit_pos = self.vm.memory[exits_pos_code + 1 + i]
            exits.append( (exit_str, exit_pos) )
        return LocationInfo(pos, name, desc, exits)

    def mark_location(self, offset, counter):
        addr = self.vm.memory[offset]
        s = str(counter)
        if len(s) < 2:
            s = '0' + s
        self.vm.memory[addr + 1] = ord(s[0])
        self.vm.memory[addr + 2] = ord(s[1])
        self.vm.memory[addr + 3] = ord('_')


    def mark_locations(self):
        counter = 0
        ranges = \
            range(2317, 2460, 5) + \
            range(2463, 2658, 5)

        for i in ranges:
            self.mark_location(i, counter)
            counter += 1


    def try_read_items(self, offset, code):
        # description of locations
        if 2317 <= offset < 2668:
            if offset < 2463:
                delta = (offset  - 2317) % 5
            else:
                delta = (offset - 2468) % 5

            if delta in [0, 1]:
                s = self.read_location_desc(offset)
                max_length = self.vm.memory[code]
                if len(s) >= LOC_LIMIT:
                    dots = '... {}'.format(max_length - LOC_LIMIT)
                else:
                    dots = ''
                s = s.replace('\n', '\\n')
                if delta == 1:
                    dd = '[raw_string]'
                if delta == 0:
                    dd = '__________'
                return '  //  {} "{}{}"'.format(dd, s, dots)
            if delta in [2, 3]:
                code = self.vm.memory[offset] # 26900 <-- code
                num_exits = self.vm.memory[code]

                if delta == 2:
                    # 26900| push 6336
                    # 26902| unknown (6344)
                    exits = []
                    for i in xrange( min(num_exits, 5) ):
                        exit_str_addr = self.vm.memory[code + 1 + i]
                        s = self.read_raw_string(exit_str_addr, limit=20)
                        exits.append(s)

                    return '  // num exits {}: {}'.format(
                        num_exits,
                        ', '.join(exits))
                if delta == 3:
                    exits = []
                    for i in xrange( min(num_exits, 5) ):
                        loc_offset = self.vm.memory[code + 1 + i]
                        s = self.read_location_desc(loc_offset)
                        exits.append('"' + s + '"')
                    return '  // locations {}: {}'.format(
                        num_exits,
                        ', '.join(exits))


        # description of items
        if 2668 <= offset < 2732:
            delta = (offset - 2668) % 4
            # 0, 1: description
            if (delta in [0, 1]):
                s = self.read_raw_string(code)
                if len(s) >= ITEM_LIMIT:
                    dots = '... {}'.format(len(s) - ITEM_LIMIT)
                else:
                    dots = ''
                s = s[:ITEM_LIMIT].replace('\n', '\\n')
                return ' //  desc: "{}{}"'.format(
                    s,
                    dots)
            # 3: location of item
            # 0 means inventory
            # X means room X
            if delta == 2:
                if code == 0:
                    return '// loc: inventory'
                if code == 32767:
                    return '// loc: ???'
                loc_offset = code
                s = self.read_location_desc(loc_offset)
                return ' // loc: "{}"'.format(
                    s
                )

        return ''


    def interpret_op(self, op, offset):
        data = op.name
        m = self.vm.memory

        if op.name == 'unknown':
            code = m[offset]
            data += ' ({})'.format(
                code,
            )
            if 32 < code < 128:
                data += ' | ' + chr(code)

            data += self.try_read_items(offset, code)
            return data

        for i in xrange(op.arity):
            value = m[offset + 1 + i]
            mem_value = read_memory(value)
            if op.name == 'out':
                if value < 256:
                    data += ' {} ({})'.format(
                        chr(value),
                        value,
                    )
                else:
                    data += ' ({})'.format(
                        mem_value
                    )
                continue
            data += ' ' + mem_value

        if op.name == 'call':
            addr = m[offset + 1]
            if addr < MEMSIZE:
                info = self.funcs[addr]
                if info is not None:
                    data += info

        # if self.funcs[offset] is not None:
        #     data += ' | ann: {} |'.format(
        #         len(self.funcs[offset])
        #     )
        if op.name == 'call':
            addr = m[offset + 1]
            if addr == 2125:
                data += '  //  unhash(r0, r1)'
            if addr == 1518:
                find_result = self.try_match_1518(offset)
                if find_result is not None:
                    data += find_result.info
                else:
                    data += '  // print_string( m[r0] )'
            if addr == 5814:
                data += '  // print_stirng("- m[r0] \\n") '

            if addr == 1458:
                find_result = self.try_match_1458_r1_1531(offset)
                if find_result is not None:
                    c = find_result.context
                    data += find_result.info
                else:
                    data += '  // for loop '

        if op.name == 'set':
            addr = m[offset + 2]
            # address in memory where list of items start
            if addr == 27381:
                data += '  // addr: list<items> (16) '


        return data

    def disasm_to_file(self, file_name):
        f = open(file_name, 'wt')
        output = self.disasm(0, None)
        f.write(output)
        f.close()



    def try_coins(self):
        coins = [
            'red coin',
            'corroded coin',
            'shiny coin',
            'concave coin',
            'blue coin',
        ]
        counter = 0
        self.vm.return_on_input = True
        for cc in permutations(coins):
            self.get_all_items()
            seq = ''
            for c in cc:
                seq += 'use ' + c + '\n'
            counter += 1
            print counter, seq.replace('\n', '\\n')

            if counter == 100:
                # self.vm.disable_output = True
                self.vm.set_input(seq)
                self.vm.run()
                # self.vm.disable_output = False

                self.vm.set_input('look\n')
                self.vm.run()


    def disasm(self, offset, limit=14):
        output = ''
        n = 0
        start_offset = offset
        offset = max(0, offset - 6)
        while offset < len(self.vm.memory):
            n += 1
            if limit is not None and n > limit:
                break

            jump, data = self.vm.try_read_out(offset)
            if not jump:
                op = self.vm.read_op(offset)
                jump = op.size()
                mem = self.vm.memory[offset : offset + op.size()]
                data = self.interpret_op(op, offset)
            # f.write("{:6}|{:>40} | {}\n".format(
            #     offset,
            #     ", ".join(map(str, mem)),
            #     data,
            # ))
            cursor = ' '
            if offset == start_offset:
                cursor = '>'
            output += "{}{:6}| {}\n".format(
                cursor,
                offset,
                # ", ".join(map(str, mem)),
                data,
            )

            offset += jump
        return output
