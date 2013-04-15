# Filter Lines plugin for Sublime Text

A Sublime Text plugin that filters lines containing a string or matching a regular expression. Searches are case sensitive by default and use the Python regular expression syntax.

Works with Sublime Text 2 and Sublime Text 3.

* [How to install](#how-to-install)
* [Available actions](#available-actions)
* [Feedback](#feedback)

## How to install ##

### Package Control ###

Install Will Bond's [Package Control](http://wbond.net/sublime_packages/package_control), and then:

* In the Command Palette, enter `Package Control: Install Package`
* Search for `Filter Lines` and install it

### Github ###

Go to your Sublime Text "Packages" directory (`Preferences` / `Browse Packages...`).

Then clone this repository:

    $ git clone https://github.com/davidpeckham/FilterLines.git

## Available actions ##

* Edit > Line > Filter To Lines Containing String:  <kbd>Ctrl+Shift+F</kbd>
* Edit > Line > Filter To Lines Matching Regex:  <kbd>Ctrl+Option+Shift+F</kbd> / <kbd>Ctrl+Alt+Shift+F</kbd>
* Edit > Code Folding > Fold To Lines Containing String
* Edit > Code Folding > Fold To Lines Matching Regex

## Preferences ##

* `case_sensitive`:  search is case sensitive by default
* `use_new_buffer_for_filter_results`:  set this to false to overwrite the current buffer

## Feedback ##

* https://github.com/davidpeckham/FilterLines/issues


![Filter Lines Demo](https://dl.dropboxusercontent.com/u/44889921/filter_lines_demo.gif)
