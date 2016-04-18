CompareOTFs
===========

A [RoboFont](https://robofont.com/) extension to diff-compare two [OpenType](https://www.microsoft.com/typography/otspec/otff.htm) font files.

![](screenshot.png)

- Uses [fontTools](https://github.com/behdad/fonttools/) to extract font tables as `.ttx` files.
- Uses Python’s [difflib](https://docs.python.org/2/library/difflib.html) to make a diff between font tables.

Installation
------------

1. [Download](https://github.com/gferreira/compare-otfs/archive/master.zip) and unzip the extension package.
2. Double-click the `.roboFontExt` file to install the extension in RoboFont.

…or get it via [Mechanic](http://robofontmechanic.com/).

Using the extension
-------------------

0. Use the *Extensions* menu in RoboFont to open the *CompareOTFs* dialog.
1. Use the *get font…* buttons to select two OpenType fonts to compare.
2. Use the *get folder…* button to choose a folder for the comparison output.
3. Use the *select tables…* button to reveal a drawer with checkboxes for all supported OpenType tables.
4. Use the checkboxes to select which tables you would like to compare.
5. Use the *compare fonts* button to generate a set of diffs for the select tables.

Note: The more tables you select, the longer it will take for the script to build all files. Some font tables like `CFF `, `CMAP` or `GPOS` are particularly long.
