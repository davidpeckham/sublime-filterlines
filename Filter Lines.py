import re

import sublime
import sublime_plugin


st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
    st_version = 3

try:
    # Python 3
    from .commands import *

except (ValueError):
    # Python 2
    from filter_to_lines_command import FilterToLinesCommand
    from fold_to_lines_command import FoldToLinesCommand
    # from commands import *
