#!/usr/bin/env python

import json
import os.path
import sys

from bs4 import BeautifulSoup
import requests

soup = BeautifulSoup(requests.get('http://www.abc.net.au/news/federal-election-2013/guide/candindex/').text)

parties = {}

for tbody in soup.findAll('tbody'):
    for row in tbody.findAll('tr'):
        last, first = [str(x) for x in row.find('td').text.split(', ', 1)]
        party = row.find('td', attrs={'class': 'party'})
        parties[party.text] = party.find('span')['title']
        party = party.text.lower()
        candidate = row.find('td', attrs={'class': 'electorate'}).text

        if first.endswith("(Sitting MP)"):
            sitting = True
            first = first[:-13]
        else:
            sitting = False

        if candidate.startswith("Senate"):
            start = candidate.find('(') + 1
            end = candidate.find(')')
            candidate = 'state/' + candidate[start:end].lower()
        else:
            end = candidate.find('(') - 1
            candidate = str(candidate[:end]).lower().translate(None, " -'")
            candidate = 'division/' + candidate

        if first == 'Ian' and last == 'McDonald':
            last = "Macdonald"

        filename = '{}-{}.json'.format(last.lower().translate(None, " -'"),
                                       first.lower().translate(None, " -'"))

        if sitting or os.path.exists('data/people/' + filename):
            data = json.loads(open('data/people/' + filename).read())
            data['candidate'] = candidate
        else:
            data = {
                'first_name': first,
                'last_name': last,
                'candidate': candidate,
            }
            if party not in ('ind', '-'):
                data['party'] = party

        # print filename
        # print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        open('data/people/' + filename, 'w').write(json.dumps(data, sort_keys=True,
            indent=4, separators=(',', ': ')))
        print open('data/people/' + filename).read()
        print ""

for code, name in parties.items():
    if code == '-':
        continue

    data = {
        'name': name,
        'code': code.upper(),
    }

    filename = '{}.json'.format(code.lower())

    open('data/parties/' + filename, 'w').write(json.dumps(data, sort_keys=True,
        indent=4, separators=(',', ': ')))
    print open('data/parties/' + filename).read()
    print ""
