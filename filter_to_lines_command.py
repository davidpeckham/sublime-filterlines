import re

import sublime
import sublime_plugin

try:
    # Python 3
    from .match import match
except (ValueError):
    # Python 2
    from match import match


st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
    st_version = 3


class FilterToLinesCommand(sublime_plugin.WindowCommand):

    def run(self, search_type = 'string'):
        self.search_type = search_type

        settings = sublime.load_settings('Filter Lines.sublime-settings')

        search_text = ""
        if settings.get('preserve_search', True):
            search_text = settings.get('latest_search', '')

        if self.search_type == 'string':
            prompt = "Filter file for lines containing: "
        else:
            prompt = "Filter file for lines matching: "

        sublime.active_window().show_input_panel(prompt, search_text, self.on_done, None, None)

    def on_done(self, text):
        if self.window.active_view():
            settings = sublime.load_settings('Filter Lines.sublime-settings')
            if settings.get('preserve_search', True):
                settings.set('latest_search', text)
            self.window.active_view().run_command("filter_to_matching_lines", { "needle": text, "search_type": self.search_type })


class FilterToMatchingLinesCommand(sublime_plugin.TextCommand):

    def filter_to_new_buffer(self, edit, needle, search_type):
        results_view = self.view.window().new_file()
        results_view.set_name('Filter Results')
        results_view.set_scratch(True)
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
                if match(needle, self.view.substr(line), search_type):
                    if st_version == 2:
                        results_view.insert(results_edit, results_view.size(), self.view.substr(line) + '\n')
                    else:
                        results_view.run_command('append', { 'characters': self.view.substr(line) + '\n', 'force': True, 'scroll_to_end': False })

        if st_version == 2:
            results_view.end_edit(results_edit)
        results_view.set_read_only(True)


    def filter_in_place(self, edit, needle, search_type):
        # get non-empty selections
        regions = [s for s in view.sel() if not s.empty()]

        # no selections? filter the whole document
        if len(regions) == 0:
            regions = [ sublime.Region(0, view.size()) ]

        for region in reversed(regions):
            lines = view.split_by_newlines(region)

            for line in reversed(lines):
                if not match(needle, view.substr(line), search_type):
                    view.erase(edit, view.full_line(line))

    def run(self, edit, needle, search_type):
        sublime.status_message("Filtering")
        settings = sublime.load_settings('Filter Lines.sublime-settings')
        if settings.get('use_new_buffer_for_filter_results', True):
            self.filter_to_new_buffer(edit, needle, search_type)
        else:
            self.filter_in_place(edit, needle, search_type)
        sublime.status_message("")

