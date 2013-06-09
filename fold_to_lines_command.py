import re

import sublime
import sublime_plugin

st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
    st_version = 3
 
try:
    # Python 3
    from .match import match_line
except (ValueError):
    # Python 2
    from match import match_line


class FoldToLinesCommand(sublime_plugin.WindowCommand):

    def run(self, search_type = 'string'):
        self.search_type = search_type

        settings = sublime.load_settings('Filter Lines.sublime-settings')

        search_text = ""
        if settings.get('preserve_search', True):
            search_text = settings.get('latest_search', '')

        invert_search = settings.get('invert_search', False)

        if self.search_type == 'string':
            prompt = "Fold to lines %s: " % ('not containing' if invert_search else 'containing')
        else:
            prompt = "Fold to lines %s regex: " % ('not matching' if invert_search else 'matching')

        sublime.active_window().show_input_panel(prompt, search_text, self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            settings = sublime.load_settings('Filter Lines.sublime-settings')
            if settings.get('preserve_search', True):
                settings.set('latest_search', text)
            self.window.active_view().run_command("fold_to_matching_lines", { "needle": text, "search_type": self.search_type })


class FoldToMatchingLinesCommand(sublime_plugin.TextCommand):

    def fold_regions(self, folds):
        region = sublime.Region(folds[0].end(), folds[0].end())
        for fold in folds:
            region = region.cover(fold)
        self.view.fold(region)


    def fold(self, edit, needle, search_type, case_sensitive, invert_search):
        # get non-empty selections
        regions = [s for s in self.view.sel() if not s.empty()]

        # no selections? filter the whole document
        if len(regions) == 0:
            regions = [ sublime.Region(0, self.view.size()) ]

        for region in reversed(regions):
            lines = self.view.split_by_newlines(region)
            folds = []

            for line in reversed(lines):

                matched = match_line(needle, self.view.substr(line), search_type, case_sensitive, invert_search)
                if matched and folds:
                    self.fold_regions(folds)
                    folds = []
                elif not matched:
                    folds.append(line)

            if folds:
                self.fold_regions(folds)

    def run(self, edit, needle, search_type):
        settings = sublime.load_settings('Filter Lines.sublime-settings')

        case_sensitive = False
        if search_type == 'string':
            case_sensitive = settings.get('case_sensitive_string_search', False)
        elif search_type == 'regex':
            case_sensitive = settings.get('case_sensitive_regex_search', True)

        invert_search = settings.get('invert_search', False)

        self.fold(edit, needle, search_type, case_sensitive, invert_search)
