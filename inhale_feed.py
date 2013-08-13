#!/usr/bin/env python

import json
import os
import os.path

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

def inhale(candidates, gvts):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    for subdir in ('people', 'party', 'group'):
        subdir = os.path.join(DATA_DIR, subdir)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

    parties = {}
    groups = {}

    candidates = BeautifulSoup(open(candidates).read(), 'xml')

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

    gvts = BeautifulSoup(open(gvts).read(), 'xml')

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
    parser.add_argument('candidates', nargs=1, help="Candidates XML file")
    parser.add_argument('gvts', nargs=1, help="Group Voting Tickets XML file")
    args = parser.parse_args()

    inhale(args.candidates[0], args.gvts[0])
