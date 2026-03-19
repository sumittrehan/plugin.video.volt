import os
import sys

# Ensure the project root is on PYTHONPATH so test imports like `resources.***` work.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
