import os, sys
# Ensure the project root is on sys.path for test imports
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)