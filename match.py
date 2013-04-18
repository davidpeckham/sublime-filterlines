import re

import sublime


def match(needle, haystack, search_type):
    settings = sublime.load_settings('Filter Lines.sublime-settings')
    case_sensitive = settings.get('case_sensitive', True)

    if search_type == "regex":
        if not case_sensitive:
            return re.search(needle, haystack, re.IGNORECASE)
        else:
            return re.search(needle, haystack)
    else:
        if not case_sensitive:
            needle = needle.upper()
            haystack = haystack.upper()

        return (needle in haystack)
