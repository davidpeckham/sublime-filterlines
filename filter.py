import itertools
import sublime
import sublime_plugin

settings_path = 'Filter Lines.sublime-settings'


class PromptFilterToLinesCommand(sublime_plugin.WindowCommand):

    def run(self, search_type='string', invert_search=False):
        self._run(search_type, 'filter_to_lines', 'Filter', invert_search)

    def _run(self, search_type, filter_command, filter_verb, invert_search):
        self.load_settings()
        self.filter_command = filter_command
        self.search_type = search_type
        self.invert_search = invert_search
        if search_type == 'string':
            prompt = "%s to lines %s: " % (
                filter_verb,
                'not containing' if self.invert_search else 'containing')
        else:
            prompt = "%s to lines %s: " % (
                filter_verb,
                'not matching' if self.invert_search else 'matching')
        if not self.search_text:
            view = self.window.active_view()
            first = view.sel()[0]  # first region (or point)
            region = first if first.size() else view.word(first.begin())
            word = view.substr(region)
            self.search_text = word
        sublime.active_window().show_input_panel(
            prompt, self.search_text, self.on_search_text_entered, None, None)

    def on_search_text_entered(self, search_text):
        self.search_text = search_text
        self.save_settings()
        if self.window.active_view():
            self.window.active_view().run_command(
                self.filter_command, {
                    "needle": self.search_text,
                    "search_type": self.search_type,
                    "invert_search": self.invert_search
                }
            )

    def load_settings(self):
        self.settings = sublime.load_settings(settings_path)
        self.search_text = ""
        if self.settings.get('preserve_search', True):
            self.search_text = self.settings.get('latest_search', '')

    def save_settings(self):
        if self.settings.get('preserve_search', True):
            self.settings.set('latest_search', self.search_text)


class FilterToLinesCommand(sublime_plugin.TextCommand):

    def run(self, edit, needle, search_type, invert_search):
        settings = sublime.load_settings(settings_path)
        flags = self.get_search_flags(search_type, settings)
        lines = itertools.groupby(
            self.view.find_all(needle, flags), self.view.line)
        lines = [l for l, _ in lines]
        self.line_numbers = settings.get('line_numbers', False)
        self.new_tab = settings.get('create_new_tab', True)
        self.invert_search = invert_search ^ (not self.new_tab)
        self.show_filtered_lines(edit, lines)

    def get_search_flags(self, search_type, settings):
        flags = 0
        if search_type == 'string':
            flags = sublime.LITERAL
            if not settings.get('case_sensitive_string_search', False):
                flags = flags | sublime.IGNORECASE
        elif search_type == 'regex':
            if not settings.get('case_sensitive_regex_search', False):
                flags = sublime.IGNORECASE
        return flags

    def show_filtered_lines(self, edit, lines):
        if self.invert_search:
            filtered_line_numbers = [
                self.view.rowcol(line.begin())[0] for line in lines
            ]
            lines = self.view.lines(sublime.Region(0, self.view.size()))
            for line_number in reversed(filtered_line_numbers):
                del lines[line_number]

        if self.new_tab:
            text = '\n'.join(
                [self.prepare_output_line(l) for l in lines]
            )
            self.create_new_tab(text)
        else:
            for line in reversed(lines):
                self.view.erase(edit, self.view.full_line(line))

    def create_new_tab(self, text):
        results_view = self.view.window().new_file()
        results_view.set_name('Filter Results')
        results_view.set_scratch(True)
        results_view.settings().set(
            'word_wrap', self.view.settings().get('word_wrap'))
        results_view.run_command(
            'append',
            {'characters': text, 'force': True, 'scroll_to_end': False}
        )
        results_view.set_syntax_file(self.view.settings().get('syntax'))

    def prepare_output_line(self, line):
        if self.line_numbers and not self.invert_search:
            line_number = self.view.rowcol(line.begin())[0]
            return '%5d: %s' % (line_number, self.view.substr(line))
        else:
            return self.view.substr(line)


class PromptFoldToLinesCommand(PromptFilterToLinesCommand):

    def run(self, search_type='string', invert_search=False):
        self._run(search_type, "fold_to_lines", "Fold", invert_search)


class FoldToLinesCommand(FilterToLinesCommand):

    def show_filtered_lines(self, edit, lines):
        source_lines = self.view.lines(sublime.Region(0, self.view.size()))
        filtered_line_numbers = {
            self.view.rowcol(line.begin())[0] for line in lines
        }
        regions = []
        region = None
        for line in source_lines:
            matched = (
                self.view.rowcol(
                    line.begin()
                )[0] in filtered_line_numbers) ^ self.invert_search
            if matched:
                if region:
                    regions.append(region)
                    region = None
            else:
                if region:
                    region = region.cover(line)
                else:
                    region = sublime.Region(line.begin(), line.end())
        if region:
            regions.append(region)
        if regions:
            self.view.fold(regions)
