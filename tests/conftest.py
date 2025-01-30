import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# os.path.dirname(__file__): return absolute path of file being run
# os.path.join( ..., ".."): add .. to the path returned above, i.e. it becomes the relative parent directory
# os.path.abspath( ... ): return the absolute path of that relative parent directory
# sys.path.insert(0, ...): adds the output to the list of directories that Python searches for modules (sys.path)