
import unittest

from vm import VM

class TestVM(unittest.TestCase):

    def test_input(self):
        ops =[9, 32768, 32769, 4, 19, 32768]
    #   - Store into register 0 the sum of 4 and the value contained in register 1.
    #   - Output to the terminal the character with the ascii code contained in register 0.
        vm = VM(ops)
        vm.r[1] = 65
        vm.run()
        self.assertEqual(vm.r[0], vm.r[1] + 4)



if __name__ == '__main__':
    unittest.main()
