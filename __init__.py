# Copy this python file as __init__.py into your project to be able to use this as a library

# To import the module copy these two lines into your project
# import __init__
# import joystickpins

from os import path
import sys
path_name = path.join(path.split(path.dirname(__file__))[0],"joystickpins")
if path_name not in sys.path:
    sys.path.insert(0, path_name)

print("adding joystickpins:", path_name)