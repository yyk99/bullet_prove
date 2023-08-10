#
#
#

import unittest
import context
from context import bulletprove


class Test_bulletprove(unittest.TestCase):

    def test_1(self):
        # print("Here...", dir(bulletprove))
        actual = bulletprove.generator.Generator()


class Test_bulletprove_Generator(unittest.TestCase):

    def test_1(self):
        actual = bulletprove.generator.Generator()
        actual.generate("out/1/2/3/4/test_1.png")


if __name__ == "__main__":
    unittest.main()
