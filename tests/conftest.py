import os
import sys

# Add the 'src' directory to sys.path so that imports like 'from tree.node import Node' resolve correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
