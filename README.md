# Filter Lines plugin for Sublime Text

A Sublime Text plugin that filters lines containing a string or matching a regular expression. Searches are case sensitive by default and use the Python regular expression syntax.

Works with Sublime Text 2 and Sublime Text 3.

* [How to install](#how-to-install)
* [Available actions](#available-actions)
* [Feedback](#feedback)
* [Demo](#demo)

## How to install ##

### Package Control ###

Install Will Bond's [Package Control](http://wbond.net/sublime_packages/package_control), and then:

* In the Command Palette, enter `Package Control: Install Package`
* Search for `Filter Lines` and install it

### Github ###

Go to your Sublime Text "Packages" directory (`Preferences` / `Browse Packages...`).

Then clone this GitHub repository:

    $ git clone https://github.com/davidpeckham/FilterLines.git "Filter Lines"

## Available actions ##

* Edit > Line > Filter With Regex:  <kbd>⌘+F</kbd> <kbd>⌘+R</kbd>
* Edit > Line > Filter With Search:  <kbd>⌘+F</kbd> <kbd>⌘+S</kbd>
* Edit > Code Folding > Fold With Regex:  <kbd>⌘+K</kbd> <kbd>⌘+R</kbd>
* Edit > Code Folding > Fold With Search:  <kbd>⌘+K</kbd> <kbd>⌘+S</kbd>

On Windows and Linux, press the <kbd>ctrl</kbd> key instead of the <kbd>⌘</kbd> key.

## Preferences ##

* `case_sensitive`:  search is case sensitive by default
* `use_new_buffer_for_filter_results`:  set this to false to overwrite the current buffer
* `preserve_search`:  if true, remembers your latest search string or regex and uses it for your next search

## Feedback ##

* https://github.com/davidpeckham/FilterLines/issues

## Demo ##

![Filter Lines Demo](https://dl.dropboxusercontent.com/u/44889921/filter_lines_demo.gif)
