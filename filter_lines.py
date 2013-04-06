
import sublime, sublime_plugin, re

def matches(needle, haystack, search_type):
    if search_type == "regex":
        return re.search(needle, haystack)
    else:
        return (needle in haystack)


def filter(view, edit, needle, search_type):
    # get non-empty selections
    regions = [s for s in view.sel() if not s.empty()]

    # no selections? filter the whole document
    if len(regions) == 0:
        regions = [ sublime.Region(0, view.size()) ]

    for region in reversed(regions):
        lines = view.split_by_newlines(region)

        for line in reversed(lines):

            if not matches(needle, view.substr(line), search_type):
                view.erase(edit, view.full_line(line))


class FilterCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.active_window().show_input_panel("Filter file for lines containing: ", "", self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            self.window.active_view().run_command("filter_lines", { "needle": text, "search_type": "string" })


class FilterUsingRegularExpressionCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.active_window().show_input_panel("Filter file for lines matching: ", "", self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            self.window.active_view().run_command("filter_lines", { "needle": text, "search_type": "regex" })


class FilterLinesCommand(sublime_plugin.TextCommand):

    def run(self, edit, needle, search_type):
        filter(self.view, edit, needle, search_type)
