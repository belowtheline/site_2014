#!/usr/bin/env python

import json

while True:
    code = raw_input('Code: ')
    if not code:
        break

    name = raw_input('Name: ')

    filename = '{}.json'.format(code.lower())

    data = {
        'name': name,
        'code': code.upper(),
    }

    open('data/parties/' + filename, 'w').write(json.dumps(data, sort_keys=True,
        indent=4, separators=(',', ': ')))
    print open('data/parties/' + filename).read()
    print ""
