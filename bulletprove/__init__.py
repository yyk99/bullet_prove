#
#
#

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print(123, __file__, os.getcwd())

import core
import generator
