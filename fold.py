import re
import sublime
import sublime_plugin
from .filter import PromptFilterToLinesCommand
from .filter import FilterToLinesCommand


class PromptFoldToLinesCommand(PromptFilterToLinesCommand):

    def run(self, search_type = 'string'):
        self._run(search_type, "fold_to_lines", "Fold")


class FoldToLinesCommand(FilterToLinesCommand):

    def show_filtered_lines(self, edit, lines):
        source_lines = self.view.lines(sublime.Region(0, self.view.size()))
        filtered_line_numbers = [self.view.rowcol(line.begin())[0] for line, _ in lines]
        regions = []
        region = None
        for line in source_lines:
            matched = (self.view.rowcol(line.begin())[0] in filtered_line_numbers) ^ self.invert_search
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

    def prepare_output_line(self, line, matches):
        pass
