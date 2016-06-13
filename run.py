from vm2 import VM2, load_bytecode
import gdb



ops = load_bytecode()
vm = VM2(ops)
vm.index = 0

# useful shortcuts
def d(offset=None, limit=15):
    if offset is None:
        offset = vm.index
    print reload(gdb).GDB(vm).disasm(offset, limit)

def p():
    vm.show_state()

# def s(limit=1):
#     vm.step(limit)

def r():
    vm.run()
    d()

def bt():
    vm.show_trace()

def n():
    vm.execute_one_op(ignore_break=True)
    d()

def x():
    return reload(gdb).GDB(vm)

def i(s):
    vm.return_on_input = True
    vm.buffer += s + '\n'
    vm.run()

def up():
    x().up()
    d()

def skip():
    op = vm.read_op(vm.index)
    next = vm.index + op.size()
    vm.break_points.add(next)
    vm.run()
    vm.break_points.remove(next)
    d()

def l(n):
    print x().get_location_info(n)

# g.disasm_to_file('asm/0.asm')
# vm.buffer += "take tablet\nuse tablet\n"
# vm.break_points.add(1841)

def preare_teleport():
    # vm.break_points.add(6027)
    vm.r[7] = 25734
    i('use teleporter')


def current_solution():
    vm.return_on_input = True
    vm.run()
    x().mark_locations()
    x().solution()

    x().disasm_to_file('asm/8.asm')
    # i('look')

def on_start():
    vm.return_on_input = True
    vm.run()
    # x().mark_locations()
    x().disasm_to_file('asm/start-2.asm')
    # i('look')

def go_to_maze():
    vm.return_on_input = True
    vm.run()
    x().mark_locations()

    x().run_seq( gdb.take_lantern_and_go_to_ladder() )
    i('look')


# go_to_maze()


# patch the memory to show all items
# 5902| eq r3 r2 r3
# 5906| jf r3 5918 --> noop noop noop
# 5909| add r0 r0 0
#
# vm.memory[5906] = 21
# vm.memory[5907] = 21
# vm.memory[5908] = 21
#

# on_start()
current_solution()

# take teleport

# x().get_all_items()
# x().solution()
# x().try_coins()
# x().disasm_to_file('asm/5.asm')

#
# # vm.block_on_output = True
# vm.buffer += "\n"


# vm.return_on_input = True
# vm.run()
#
# # g().analyze()
# # g().disasm_to_file('asm/4.asm')
# vm.return_on_input = False

# commands = [
#     'doorway',
#     'north',
#     'north',
#     'bridge',
#     'continue',
#     'down',
#     'east',
#     'take empty lantern',
#     'west',
#     'west',
#     'passage',
# ]
# for cmd in commands:
#     vm.buffer += (cmd + '\n')
# vm.run()
