
import sublime, sublime_plugin, re


st_version = 2

if sublime.version() == '' or int(sublime.version()) > 3000:
    st_version = 3


def matches(needle, haystack, search_type):
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


class FilterLinesCommand(sublime_plugin.WindowCommand):

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
                if matches(needle, self.view.substr(line), search_type):
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
                if not matches(needle, view.substr(line), search_type):
                    view.erase(edit, view.full_line(line))

    def run(self, edit, needle, search_type):
        sublime.status_message("Filtering")
        settings = sublime.load_settings('Filter Lines.sublime-settings')
        if settings.get('use_new_buffer_for_filter_results', True):
            self.filter_to_new_buffer(edit, needle, search_type)
        else:
            self.filter_in_place(edit, needle, search_type)
        sublime.status_message("")


class FoldToFilteredLinesCommand(sublime_plugin.WindowCommand):

    def run(self, search_type = 'string'):
        self.search_type = search_type

        settings = sublime.load_settings('Filter Lines.sublime-settings')

        search_text = ""
        if settings.get('preserve_search', True):
            search_text = settings.get('latest_search', '')

        if self.search_type == 'string':
            prompt = "Fold to lines containing: "
        else:
            prompt = "Fold to lines matching: "

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


    def fold(self, edit, needle, search_type):
        # get non-empty selections
        regions = [s for s in self.view.sel() if not s.empty()]

        # no selections? filter the whole document
        if len(regions) == 0:
            regions = [ sublime.Region(0, self.view.size()) ]

        for region in reversed(regions):
            lines = self.view.split_by_newlines(region)
            folds = []

            for line in reversed(lines):

                matched = matches(needle, self.view.substr(line), search_type)
                if matched and folds:
                    self.fold_regions(folds)
                    folds = []
                else:
                    folds.append(line)

            if folds:
                self.fold_regions(folds)

    def run(self, edit, needle, search_type):
        self.fold(edit, needle, search_type)
