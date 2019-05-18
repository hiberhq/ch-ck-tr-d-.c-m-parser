#!/usr/bin/env/ python3

import os
import json

RESULT = 'data.json'


def log(text, color = ''):
	colors = {
		'black': '\x1b[30m',
		'red': '\x1b[31m',
		'green': '\x1b[32m',
		'yellow': '\x1b[33m',
		'blue': '\x1b[34m',
		'magenta': '\x1b[35m',
		'cyan': '\x1b[36m',
		'white': '\x1b[37m'
	}
	print(colors.get(color, '\x1b[0m'), text, '\x1b[0m')

log('...Cleaning up duplicates...', 'magenta')
unique = []
with open(RESULT, 'r') as file:
	data = json.loads(file.read())

for item in data:

	if len(unique):
		for i, u in enumerate(unique):
			if item['name'] == u['name'] and item['email'] == u['email']:
				break
			else:
				if i == len(unique) - 1:
					unique.append(item)
	else:
		unique.append(item)
	
log('...DONE! %s duplicates were removed. %s companies are unique.' % (len(data) - len(unique), len(unique)), 'yellow')

with open(RESULT, 'w') as file:
	file.write(json.dumps(unique))
# Save it just in case
with open('original_data.json', 'w') as file:
	file.write(json.dumps(data))