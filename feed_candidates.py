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
    for subdir in ('people', 'party'):
        subdir = os.path.join(DATA_DIR, subdir)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

    preload = zipfile.ZipFile(preload)
    for name in preload.namelist():
        if name.startswith('xml/eml-230'):
            break
    candidates = BeautifulSoup(preload.open(name).read(), 'xml')
    preload.close()

    parties = {}

    for contest in candidates.find_all('Contest'):
        division = contest.find('ContestName').text
        if division in STATES:
            division = STATES[division]
        else:
            division = division_name(division)

        for candidate in contest.find_all('Candidate'):
            last, first = candidate.find('CandidateName').text.split(', ', 1)
            party = candidate.find('Affiliation')

            code = None
            if candidate['Independent'].lower() != 'yes' and party is not None:
                code = party.find('AffiliationIdentifier')['ShortCode'].lower()
                if code not in parties:
                    parties[code] = {
                        'name': party.find('RegisteredName').text,
                        'code': party.find('AffiliationIdentifier')['ShortCode'].upper(),
                    }

            filename = os.path.join(DATA_DIR, candidate_id(first, last))
            filename += '.json'
            with open(filename, 'w') as out:
                data = {
                    'first_name': first,
                    'last_name': last,
                    'candidate': division,
                }
                if code is not None:
                    data['party'] = code

                out.write(jsonify(data))

    for party_id, data in parties.items():
        filename = os.path.join(DATA_DIR, 'party', party_id) + '.json'
        open(filename, 'w').write(jsonify(data))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('preload', nargs=1, help="AEC preload Zip archive")
    args = parser.parse_args()

    inhale(args.preload[0])
