# Requirements
## Python 3
To check if it is installed:

`python3 --version`

## pip3
To check if it is installed:

`pip3`

Otherwise install them. The way depends on platform.

# Install dependecies
`$ pip3 install requests`

`$ pip3 install bs4`

# Usage
By running

`$ python3 p.py`

the parser will continue from the last state. Or will just start it initially if this is the first launch.

`$ python3 p.py -f`

will start to working from the ground erasing the previous parser state and all parsed data.

Files `postcodes.conf` / `categories.conf` have postcodes/categories for current task. This is the thing you have to adjust before running.
Values should be written in one line and separated by commas. If `postcodes.conf` / `categories.conf` doesn't exist `postcodes_all.conf` / `categories_all.conf` will be used insted.
But `postcodes.conf` / `categories.conf` have priority.

# Result
The data will be written to `data.json` and represents array of objects. Note that data will have a lot of duplicates regardless of the script. So they must be cleaned the way depends on how the data will be used.

![Done](screenshot.png?raw=true)

# Advanced
The `temp/state.json` stores the current parser state and has `page` (for search results page) `postcode` and `cat` (indexes of current postcode/category in current array of postcodes/categories). So they can be scpecified manually before the parser is launched to start from some position.