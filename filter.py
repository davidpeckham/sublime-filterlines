import functools
import itertools
import re
import sublime
import sublime_plugin

settings_path = 'Filter Lines.sublime-settings'

class PromptFilterToLinesCommand(sublime_plugin.WindowCommand):

    def run(self, search_type = 'string'):
        self._run(search_type, "filter_to_lines", "Filter")

    def _run(self, search_type, filter_command, filter_verb):
        self.load_settings()
        self.filter_command = filter_command
        self.search_type = search_type
        if search_type == 'string':
            prompt = "%s to lines %s: " % (filter_verb, 'not containing' if self.invert_search else 'containing')
        else:
            prompt = "%s to lines %s: " % (filter_verb, 'not matching' if self.invert_search else 'matching')
        sublime.active_window().show_input_panel(prompt, self.search_text, self.on_search_text_entered, None, None)

    def on_search_text_entered(self, search_text):
        self.search_text = search_text
        self.save_settings()
        if self.window.active_view():
            self.window.active_view().run_command(self.filter_command, { 
                "needle": self.search_text, "search_type": self.search_type })

    def load_settings(self):
        self.settings = sublime.load_settings(settings_path)
        self.search_text = ""
        if self.settings.get('preserve_search', True):
            self.search_text = self.settings.get('latest_search', '')
        self.invert_search = self.settings.get('invert_search', False)

    def save_settings(self):
        if self.settings.get('preserve_search', True):
            self.settings.set('latest_search', self.search_text)


class FilterToLinesCommand(sublime_plugin.TextCommand):

    def run(self, edit, needle, search_type):
        settings = sublime.load_settings(settings_path)
        self.invert_search = settings.get('invert_search', False)
        flags = self.get_search_flags(search_type, settings)
        lines = itertools.groupby(self.view.find_all(needle, flags), self.view.line)
        self.line_numbers = settings.get('line_numbers', False)
        self.show_filtered_lines(edit, lines)

    def get_search_flags(self, search_type, settings):
        flags = 0
        if search_type == 'string':
            flags = sublime.LITERAL
            if not settings.get('case_sensitive_string_search', False):
                flags = flags | sublime.IGNORECASE
        elif search_type == 'regex':
            if not settings.get('case_sensitive_string_search', False):
                flags = sublime.IGNORECASE
        return flags

    def show_filtered_lines(self, edit, lines):
        results_view = self.view.window().new_file()
        results_view.set_name('Filter Results')
        results_view.set_scratch(True)
        results_view.settings().set('word_wrap', self.view.settings().get('word_wrap'))

        if self.invert_search:
            source_lines = self.view.lines(sublime.Region(0, self.view.size()))
            filtered_line_numbers = [self.view.rowcol(line.begin())[0] for line, _ in lines]
            for line_number in reversed(filtered_line_numbers):
                del source_lines[line_number]
            text = ''
            for line in source_lines:
                text += self.prepare_output_line(line, None)
            results_view.run_command('append', {'characters': text, 'force': True, 'scroll_to_end': False})
        else:
            text = ''
            for line, matches in lines:
                text += self.prepare_output_line(line, matches)
            results_view.run_command('append', {'characters': text, 'force': True, 'scroll_to_end': False})

        results_view.set_syntax_file(self.view.settings().get('syntax'))

    def prepare_output_line(self, line, matches):
        if self.line_numbers and not self.invert_search:
            line_number = self.view.rowcol(line.begin())[0]
            return '%5d: %s\n' % (line_number, self.view.substr(line))
        else:
            return '%s\n' % (self.view.substr(line))
