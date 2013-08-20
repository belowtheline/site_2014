#!/usr/bin/env python

import json
import os
import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

ballots = {
    'act': [],
    'nsw': [],
    'nt': [],
    'qld': [],
    'sa': [],
    'tas': [],
    'vic': [],
    'wa': [],
}
people = {}
parties = {}
divisions = {}

def sorted_candidates(candidates):
    return [c[:-1] for c in sorted(candidates, key=lambda x: x[3])]

for filename in os.listdir('data/people'):
    if not filename.endswith('.json'):
        continue

    person_id = filename[:-5]
    people[person_id] = json.loads(open('data/people/' + filename).read())

for filename in os.listdir('data/parties'):
    if not filename.endswith('.json'):
        continue

    party_id = filename[:-5]
    parties[party_id] = json.loads(open('data/parties/' + filename).read())

for filename in os.listdir('data/division'):
    if not filename.endswith('.json'):
        continue

    division_id = filename[:-5]
    divisions[division_id] = json.loads(open('data/division/' + filename).read())

for state in ('act', 'nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa'):
    ungrouped = {
        'label': 'UG',
        'name': 'Ungrouped',
        'candidates': [],
    }

    for filename in os.listdir('data/groups'):
        if not filename.startswith(state):
            continue
        if not filename.endswith('.json'):
            continue

        group = json.loads(open('data/groups/' + filename).read())
        group_label = filename[:-5].split('-', 1)[1]
        ballot = ballots[state]

        if group_label.startswith('UG'):
            ballot_group = ungrouped
        else:
            ballot_group = {
                'label': group_label,
                'name': group['name'],
            }
            ballot.append(ballot_group)
        
        candidates = []
        for candidate in group['candidates']:
            person = people[candidate]

            if person.get('party', None) is not None:
                c = (person['last_name'], person['first_name'],
                     parties[person['party']]['name'], person['ballot_position'])
            else:
                c = (person['last_name'], person['first_name'], None,
                     person['ballot_position'])
            candidates.append(c)

        if group_label.startswith('UG'):
            ungrouped['candidates'].append(candidates[0][:-1])
        else:
            ballot_group['candidates'] = sorted_candidates(candidates)

    if ungrouped['candidates']:
        ballots[state].append(ungrouped)

division_ballots = {}

for person_id, person in people.items():
    if 'candidate' not in person:
        continue
    if not person['candidate'].startswith('division/'):
        continue

    division = person['candidate'].split('/')[1]
    if division not in division_ballots:
        division_ballots[division] = []

    if person.get('party', None) is not None:
        c = (person['last_name'], person['first_name'],
             parties[person['party']]['name'], person['ballot_position'])
    else:
        c = (person['last_name'], person['first_name'], None,
             person['ballot_position'])

    division_ballots[division].append(c)

def group_sort(a, b):
    a = a['label']
    b = b['label']

    if len(a) != len(b):
        return cmp(len(a), len(b))
    else:
        return cmp(a, b)

for state in ballots:
    ballots[state].sort(group_sort)        

for division, candidates in division_ballots.items():
    ballots[division] = (divisions[division]['name'],
                         sorted_candidates(candidates))

pickle.dump(ballots, open('ballots.pck', 'w'))
