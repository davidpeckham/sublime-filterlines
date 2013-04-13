
import sublime, sublime_plugin, re


def matches(needle, haystack, search_type):
    settings = sublime.load_settings('Filter Lines.sublime-settings')

    if not settings.get('case_sensitive', True):
        needle = needle.upper()
        haystack = haystack.upper()

    if search_type == "regex":
        return re.search(needle, haystack)
    else:
        return (needle in haystack)


def filter(view, edit, needle, search_type):
    settings = sublime.load_settings('Filter Lines.sublime-settings')
    results_in_new_window = settings.get('show_results_in_new_buffer', False)
    if results_in_new_window:
        results_view = view.window().new_file()
        results_view.set_name(needle)
        results_edit = results_view.begin_edit()

    # get non-empty selections
    regions = [s for s in view.sel() if not s.empty()]

    # no selections? filter the whole document
    if len(regions) == 0:
        regions = [ sublime.Region(0, view.size()) ]

    for region in reversed(regions):
        lines = view.split_by_newlines(region)

        for line in reversed(lines):
            matched = matches(needle, view.substr(line), search_type)
            if matched and results_in_new_window:
                results_view.insert(results_edit, 0, view.substr(line) + '\n')
            elif not matched and not results_in_new_window:
                view.erase(edit, view.full_line(line))

    if results_in_new_window:
        results_view.end_edit(results_edit)
        view.window().focus_view(results_view)


class FilterToLinesContainingStringCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.active_window().show_input_panel("Filter file for lines containing: ", "", self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            self.window.active_view().run_command("filter_to_matching_lines", { "needle": text, "search_type": "string" })


class FilterToLinesMatchingRegexCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.active_window().show_input_panel("Filter file for lines matching: ", "", self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            self.window.active_view().run_command("filter_to_matching_lines", { "needle": text, "search_type": "regex" })


class FilterToMatchingLinesCommand(sublime_plugin.TextCommand):

    def run(self, edit, needle, search_type):
        sublime.status_message("Filtering")
        filter(self.view, edit, needle, search_type)
        sublime.status_message("")



def fold_regions(view, folds):
    region = sublime.Region(folds[0].end(), folds[0].end())
    for fold in folds:
        region = region.cover(fold)
    view.fold(region)


def fold(view, edit, needle, search_type):
    # get non-empty selections
    regions = [s for s in view.sel() if not s.empty()]

    # no selections? filter the whole document
    if len(regions) == 0:
        regions = [ sublime.Region(0, view.size()) ]

    for region in reversed(regions):
        lines = view.split_by_newlines(region)
        # region_to_fold = sublime.Region(region.end(), region.end())
        folds = []

        for line in reversed(lines):

            matched = matches(needle, view.substr(line), search_type)
            if matched:
                fold_regions(view, folds)
                folds = []
            else:
                folds.append(line)

        if folds:
            fold_regions(view, folds)


class FoldToLinesContainingStringCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.active_window().show_input_panel("Fold to lines containing: ", "", self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            self.window.active_view().run_command("fold_to_matching_lines", { "needle": text, "search_type": "string" })


class FoldToLinesMatchingRegexCommand(sublime_plugin.WindowCommand):

    def run(self):
        sublime.active_window().show_input_panel("Fold to lines matching: ", "", self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            self.window.active_view().run_command("fold_to_matching_lines", { "needle": text, "search_type": "regex" })


class FoldToMatchingLinesCommand(sublime_plugin.TextCommand):

    def run(self, edit, needle, search_type):
        fold(self.view, edit, needle, search_type)

