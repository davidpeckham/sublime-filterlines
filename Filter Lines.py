import re

import sublime
import sublime_plugin


try:
    # Python 3
    from .filter_to_lines_command import *
    from .fold_to_lines_command import *

except (ValueError):
    # Python 2
    from filter_to_lines_command import *
    from fold_to_lines_command import *

