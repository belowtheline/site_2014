#!/usr/bin/env python

import json
import os
import os.path
import zipfile

from bs4 import BeautifulSoup

DATA_DIR = 'newdata'

STATES = {
    'Australian Capital Territory': 'state/act',
    'New South Wales': 'state/nsw',
    'Victoria': 'state/vic',
    'Queensland': 'state/qld',
    'Western Australia': 'state/wa',
    'South Australia': 'state/sa',
    'Northern Territory': 'state/nt',
    'Tasmania': 'state/tas',
}

ID_TRANSLATION = {
    ord(u' '): None,
    ord(u'-'): None,
    ord(u"'"): None,
}

def division_name(name):
    return 'division/' + name.lower().translate(ID_TRANSLATION)

def candidate_id(first, last):
    first = first.lower().translate(ID_TRANSLATION)
    last = last.lower().translate(ID_TRANSLATION)
    return 'people/{}-{}'.format(last, first)

def group_id(state, code):
    return 'group/{}-{}'.format(state.split('/')[1], code.lower())

def jsonify(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))

def inhale(preload):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    subdir = os.path.join(DATA_DIR, 'group')
    if not os.path.exists(subdir):
        os.mkdir(subdir)

    preload = zipfile.ZipFile(preload)
    for name in preload.namelist():
        if name.startswith('xml/aec-mediafeed-groupvotingtickets'):
            break
    gvts = BeautifulSoup(preload.open(name).read(), 'xml')
    preload.close()

    groups = {}

    for contest in gvts.find_all('Contest'):
        state = STATES[contest.find('ContestName').text]

        for group in contest.find_all('Group'):
            data = {
                'code': group.find('Ticket').text,
                'name': group.find('GroupName').text,
                'candidates': [],
                'tickets': [],
            }

            for candidate in group.find_all('Candidate', recursive=False):
                last, first = candidate.find('CandidateName').text.split(', ', 1)
                data['candidates'].append(candidate_id(first, last))
                assert os.path.exists(os.path.join(DATA_DIR, candidate_id(first, last)) + '.json')

            for ticket in group.find_all('GroupVotingTicket'):
                ticket_data = {}

                for candidate in ticket.find_all('Candidate'):
                    last, first = candidate.find('CandidateName').text.split(', ', 1)
                    preference = int(candidate.find('Preference').text)
                    ticket_data[preference] = candidate_id(first, last)

                ticket_data = [ticket_data[p] for p in sorted(ticket_data)]
                data['tickets'].append(ticket_data)

            filename = os.path.join(DATA_DIR, group_id(state, data['code']))
            filename += '.json'
            open(filename, 'w').write(jsonify(data))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('preload', nargs=1, help="AEC preload Zip archive")
    args = parser.parse_args()

    inhale(args.preload[0])
