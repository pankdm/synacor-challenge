
import sys

from ops import *
from util import *
from copy import copy
from teleport import f4_1


class FrameInfo:
    def __init__(self):
        self.jump = 0
        self.ret = 0
        self.name = ''
        self.r = []

    def __str__(self):
        return '({}), ret = {}'.format(
            self.name,
            self.ret
        )

class Break(Exception):
    def __init__(self, value):
        self.value = value

class VM2:
    def __init__(self, ops):
        self.ops = ops

        # setup memory
        self.memory = [0] * MEMSIZE
        for i in xrange(len(self.ops)):
            self.memory[i] = self.ops[i]

        self.r = [0] * 8
        self.stack = []
        self.meta_stack = []

        self.index = 0

        self.stop = False

        self.buffer = ""
        self.bi = 0

        self.log = open('log.txt', 'wt')

        self.return_on_input = False
        self.block_on_output = False
        self.disable_output = False
        self.stop_on_return = False
        self.use_fast_6027 = True
        self.depth = 0

        self.cpu = 0

        self.output = []

        self.call_stack = []
        self.break_points = set()

    def read_op(self, offset):
        op_code = self.memory[offset]
        if op_code in CODES:
            return CODES[op_code]
        else:
            return OpSpec.unknown()

    def show_program(self, offset, limit=10):
        for i in xrange(limit):
            op = self.read_op(offset)
            print "{} |    {} {}".format(
                offset,
                op.name,
                op.args,
            )
            offset += op.size()

    def try_read_out(self, offset):
        jump = 0
        stop = False
        s = ''
        while not stop:
            op = self.read_op(offset)
            stop = True
            if op.name == 'out':
                value = self.memory[offset + 1]
                if value < 256:
                    if value == 10:
                        s += '\\n'
                    else:
                        s += chr(value)
                    stop = False
                    offset += 2
                    jump += 2

        data = 'out "{}"'.format(s)
        return jump, data




    def get_value(self, v):
        if v < MAX_VALUE:
            return v
        return self.r[ v - MAX_VALUE ]

    def write_r(self, a, value):
        self.r[ a - MAX_VALUE ] = value


    def read(self, num):
        res = self.memory[self.index : self.index + num]
        self.index += num
        if num == 1:
            return res[0]
        return res

    def set_input(self, buffer):
        self.buffer = buffer
        self.bi = 0

    def get_char(self):
        if self.bi >= len(self.buffer):
            if self.return_on_input:
                # restore 2 read symbols
                self.index -= 2
                raise Break('>: returned while reading from stdin')

            input = raw_input('>:')
            if input == '?':
                # restore 2 read symbols
                self.index -= 2
                raise Break('>: returned back to shell')

            self.buffer += input + '\n'
            # print "Read line {} (len = {}) from console".format(
            #     self.buffer,
            #     len(self.buffer),
            # )
            # self.bi = 0

        char = self.buffer[self.bi]
        self.bi += 1

        # print "Read {} from console".format(
        #     ord(char)
        # )
        return char

    def show_state(self):
        index = self.index
        print
        print "index = {}, cpu step = {}".format(
            index,
            self.cpu)
        for i in xrange(len(self.r)):
            print "r{}: {}".format(i, self.r[i])
        # print 'stack ({}): {}'.format(len(self.stack), self.stack)
        data = 'stack ({}): '.format(len(self.stack))
        vals = []
        for i in xrange(len(self.stack)):
            vals.append('{}({})'.format(
                self.stack[i],
                self.meta_stack[i],
            ))
        data += '[' + ', '.join(vals) + ']'
        print data

        self.show_output()

    def show_output(self, limit=20):
        print 'output: "{}"'.format(
            ''.join(self.output[-limit:])
        )

    def dump_state(self):
        i = self.index
        if TRACE:
            print >> self.log
            print >> self.log, "index = ", i
            print >> self.log, "Registers: ", self.r
            print >> self.log, "Memory: ", self.memory[i: i + 5]

    def execute_one_op(self, ignore_break=False):
        i = self.index
        m = self.memory[i]

        if not ignore_break:
            if i in self.break_points:
                raise Break('Stop on {}'.format(i))

        if self.use_fast_6027 and i == 6027:
            r0 = self.r[0]
            r1 = self.r[1]
            r7 = self.r[7]

            ok = (r0 == 4 and r1 == 1)
            if not ok:
                raise Break(
                    'Unexpected args to 6027: (r0 = {}, r1 = {})'.format(
                        r0, r1
                    ))

            a = f4_1(r7)
            print 'Got {} for {}'.format(a, (r0, r1, r7) )
            # code around:
            #>6027| jt r0 6035  # if A == 0
            # 6030| add r0 r1 1 # r0 = r1 + 1
            # 6034| ret

            # so we go to next instructions
            self.r[1] = mod(a - 1)
            self.index = 6030
            return

        op = self.read(1)
        r = self.r
        if op == 0:
            # halt: 0
            #   stop execution and terminate the program
            name = 'halt'
            self.stop = True
        elif op == 1:
            # set: 1 a b
            #   set register <a> to the value of <b>
            name = 'set'
            a, b = self.read(2)
            self.write_r(a, self.get_value(b))
        elif op == 2:
            # push: 2 a
            #   push <a> onto the stack
            name = 'push'
            a = self.read(1)

            self.stack.append( self.get_value(a) )
            self.meta_stack.append( read_memory(a) )
        elif op == 3:
            # pop: 3 a
            #   remove the top element from the stack and write it into <a>; empty stack = error
            name = 'pop'
            a = self.read(1)
            self.write_r(a, self.stack.pop() )
            self.meta_stack.pop()
        elif op == 4:
            # eq: 4 a b c
            #   set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
            name = 'eq'
            a, b, c = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            if vb == vc:
                self.write_r(a, 1)
            else:
                self.write_r(a, 0)
        elif op == 5:
            # gt: 5 a b c
            #   set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
            name = 'gt'
            a, b, c, = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            if vb > vc:
                self.write_r(a, 1)
            else:
                self.write_r(a, 0)
        elif op == 6:
            # jmp: 6 a
            #   jump to <a>
            name = 'jmp'
            a = self.read(1)
            self.index = self.get_value(a)
        elif op == 7:
            # jt: 7 a b
            #   if <a> is nonzero, jump to <b>
            name = 'jt'
            a, b = self.read(2)
            if self.get_value(a) != 0:
                self.index = self.get_value(b)
        elif op == 8:
            # jf: 8 a b
            #   if <a> is zero, jump to <b>
            name = 'jf'
            a, b = self.read(2)
            if self.get_value(a) == 0:
                self.index = self.get_value(b)
        elif op == 9:
            # add: 9 a b c
            #   assign into <a> the sum of <b> and <c> (modulo 32768)
            name = 'add'
            a, b, c = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            self.write_r(a, mod(vb + vc) )
        elif op == 10:
            # mult: 10 a b c
            #   store into <a> the product of <b> and <c> (modulo 32768)
            name = 'mult'
            a, b, c = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            self.write_r(a, mod(vb * vc) )
        elif op == 11:
            # mod: 11 a b c
            #   store into <a> the remainder of <b> divided by <c>
            name = 'mod'
            a, b, c = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            self.write_r(a, vb % vc)
        elif op == 12:
            # and: 12 a b c
            #   stores into <a> the bitwise and of <b> and <c>
            name = 'and'
            a, b, c = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            self.write_r(a, vb & vc)
        elif op == 13:
            # or: 13 a b c
            #   stores into <a> the bitwise or of <b> and <c>
            name = 'or'
            a, b, c = self.read(3)
            vb = self.get_value(b)
            vc = self.get_value(c)
            self.write_r(a, vb | vc)
        elif op == 14:
            # not: 14 a b
            #   stores 15-bit bitwise inverse of <b> in <a>
            name = 'not'
            a, b = self.read(2)
            vb = inverse( self.get_value(b) )
            self.write_r(a, vb)
        elif op == 15:
            # rmem: 15 a b
            #   read memory at address <b> and write it to <a>
            name = 'rmem'
            a, b = self.read(2)
            self.write_r(a, self.memory[ self.get_value(b) ])
        elif op == 16:
            # wmem: 16 a b
            #   write the value from <b> into memory at address <a>
            name = 'wmem'
            a, b = self.read(2)
            self.memory[ self.get_value(a) ] = self.get_value(b)
        elif op == 17:
            # call: 17 a
            #   write the address of the next instruction to the stack and jump to <a>
            name = 'call'
            a = self.read(1)

            self.stack.append(self.index)

            meta = 'call {}'.format(self.get_value(a))
            self.meta_stack.append( meta )

            addr = self.get_value(a)
            self.trace_call(addr, meta)

            self.depth += 1

            self.index = addr
        elif op == 18:
            if self.stop_on_return and self.depth == 0:
                self.index -= 1
                raise Break('Returning from function')

            self.depth -= 1
            # ret: 18
            #   remove the top element from the stack and jump to it; empty stack = halt
            name = 'ret'
            if not self.stack:
                print 'empty stack = halt, while executing "ret"'
                self.stop = True
            else:
                self.index = self.stack.pop()
                self.meta_stack.pop()
                self.trace_return()
        elif op == 19:
            # out: 19 a
            #   write the character represented by ascii code <a> to the terminal
            name = 'out'
            a = self.read(1)
            char = chr(self.get_value(a))

            if not self.disable_output:
                sys.stdout.write( char )

            self.output.append( char )

            if self.block_on_output:
                raise Break('Interruption while outputting')

        elif op == 20:
            # in: 20 a
            #   read a character from the terminal and write its ascii code to <a>;
            #   it can be assumed that once input starts, it will continue until
            #   a newline is encountered; this means that you can safely read
            #   whole lines from the keyboard and trust that they will be fully read
            name = 'in'
            # print "Found input: exiting"
            # self.stop = True
            # return

            a = self.read(1)
            char = self.get_char()
            self.write_r(a, ord(char) )
        elif op == 21:
            # noop: 21
            #   no operation
            name = 'noop'

        self.cpu += 1
        # if TRACE:
        #     print >> self.log, 'Executing {} ({}) at {}'.format(
        #         m,
        #         name,
        #         i,
        #     )

    def trace_call(self, addr, meta):
        frame = FrameInfo()
        frame.name = meta
        frame.jump = addr
        frame.ret = self.index
        frame.r = copy(self.r)

        self.call_stack.append(frame)

    def trace_return(self):
        self.call_stack.pop()

    def show_trace(self):
        num = 0
        for i in reversed(xrange(len(self.call_stack))):
            print '#{}: {}'.format(
                num,
                str(self.call_stack[i]),
            )
            num += 1


    def run(self):
        try:
            while True:
                if self.stop:
                    print 'Program halted'
                    break
                # self.dump_state()
                self.execute_one_op()
        except Break as e:
            print 'Caught exception: ', e.value


    def step(self, limit):
        try:
            for i in xrange(limit):
                if self.stop:
                    print 'Program halted'
                    break
                self.execute_one_op()
        except Break as e:
            print 'Caught exception: ', e.value
