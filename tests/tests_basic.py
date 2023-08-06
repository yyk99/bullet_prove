#
#
#

import unittest
import context
from context import bulletprove


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_isupper(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


class TestBulletprove(unittest.TestCase):

    def test_1(self):
        # print("Here...", dir(bulletprove))
        actual = bulletprove.generator.Generator()


if __name__ == "__main__":
    unittest.main()
