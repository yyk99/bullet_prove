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

    def test_2(self):
        actual = bulletprove.generator.Generator()
        for i in range(10):
            actual.generate(f"out/test_2/test_{i}.png")

    def test_3(self):
        actual = bulletprove.generator.Generator(n_points=5)
        actual.generate(f"out/test_3/dots.png")


if __name__ == "__main__":
    unittest.main()
