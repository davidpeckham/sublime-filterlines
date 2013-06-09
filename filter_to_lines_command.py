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


class FilterToLinesCommand(sublime_plugin.WindowCommand):

    def run(self, search_type = 'string'):
        self.search_type = search_type

        settings = sublime.load_settings('Filter Lines.sublime-settings')

        search_text = ""
        if settings.get('preserve_search', True):
            search_text = settings.get('latest_search', '')

        invert_search = settings.get('invert_search', False)

        if self.search_type == 'string':
            prompt = "Filter file for lines %s: " % ('not containing' if invert_search else 'containing')
        else:
            prompt = "Filter file for lines %s regex: " % ('not matching' if invert_search else 'matching')


        sublime.active_window().show_input_panel(prompt, search_text, self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            settings = sublime.load_settings('Filter Lines.sublime-settings')
            if settings.get('preserve_search', True):
                settings.set('latest_search', text)
            self.window.active_view().run_command("filter_to_matching_lines", { "needle": text, "search_type": self.search_type })


class FilterToMatchingLinesCommand(sublime_plugin.TextCommand):

    def filter_to_new_buffer(self, edit, needle, search_type, case_sensitive, invert_search):
        results_view = self.view.window().new_file()
        results_view.set_name('Filter Results')
        results_view.set_scratch(True)
        results_view.settings().set('word_wrap', self.view.settings().get('word_wrap'))
        if st_version == 2:
            results_edit = results_view.begin_edit()

        # get non-empty selections
        regions = [s for s in self.view.sel() if not s.empty()]

        # no selections? filter the whole document
        if len(regions) == 0:
            regions = [ sublime.Region(0, self.view.size()) ]

        for region in regions:
            lines = self.view.split_by_newlines(region)

            for line in lines:
                if match_line(needle, self.view.substr(line), search_type, case_sensitive, invert_search):
                    if st_version == 2:
                        results_view.insert(results_edit, results_view.size(), self.view.substr(line) + '\n')
                    else:
                        results_view.run_command('append', { 'characters': self.view.substr(line) + '\n', 'force': True, 'scroll_to_end': False })

        if results_view.size() > 0:
            results_view.set_syntax_file(self.view.settings().get('syntax'))
        else:
            message = 'Filtering lines for "%s" %s\n\n0 matches\n' % (needle, '(case-sensitive)' if case_sensitive else '(not case-sensitive)')
            if st_version == 2:
                results_view.insert(results_edit, results_view.size(), message)
            else:
                results_view.run_command('append', { 'characters': message, 'force': True, 'scroll_to_end': False })

        if st_version == 2:
            results_view.end_edit(results_edit)


    def filter_in_place(self, edit, needle, search_type, case_sensitive, invert_search):
        # get non-empty selections
        regions = [s for s in view.sel() if not s.empty()]

        # no selections? filter the whole document
        if len(regions) == 0:
            regions = [ sublime.Region(0, view.size()) ]

        for region in reversed(regions):
            lines = view.split_by_newlines(region)

            for line in reversed(lines):
                if not match_line(needle, view.substr(line), search_type, case_sensitive, invert_search):
                    view.erase(edit, view.full_line(line))


    def run(self, edit, needle, search_type):
        sublime.status_message("Filtering")
        settings = sublime.load_settings('Filter Lines.sublime-settings')

        case_sensitive = False
        if search_type == 'string':
            case_sensitive = settings.get('case_sensitive_string_search', False)
        elif search_type == 'regex':
            case_sensitive = settings.get('case_sensitive_regex_search', True)

        invert_search = settings.get('invert_search', False)

        if settings.get('use_new_buffer_for_filter_results', True):
            self.filter_to_new_buffer(edit, needle, search_type, case_sensitive, invert_search)
        else:
            self.filter_in_place(edit, needle, search_type, case_sensitive, invert_search)

        sublime.status_message("")

