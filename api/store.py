from datetime import timedelta
from functools import update_wrapper

import marshal
import random
import string

from flask import Flask, abort, current_app, jsonify, make_response, request
import redis

ID_ALPHABET = ''.join([string.lowercase, string.uppercase, string.digits,
                       '~!@$%^*()-_=+<>,.|'])
REDIS_HOST = 'localhost'
REDIS_DB = 5
MAX_TRIES = 10

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def store_at_random_id(ballot, start_length=5):
    r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)
    candidate = None
    n = start_length
    tries = 0

    def store(c):
        if c is None:
            return False

        for reserved in RESERVED:
            if c.startswith(reserved):
                return False

        for key in sorted(ballot.keys()):
            if not r.hsetnx(c, key, ballot[key]):
                return False

        return True

    while not store(candidate):
        candidate = ''.join(random.choice(ID_ALPHABET) for x in range(0, n))
        tries += 1
        if tries > MAX_TRIES:
            n += 1
            tries = 0

    return candidate

@app.route('/store', methods=['POST', 'OPTIONS'])
@crossdomain(origin=['http://localhost:8000'], headers=['Content-Type', 'X-Requested-With'])
def store_ballot():
    if request.json is not None:
        state = request.json['state']
        division = request.json['division']
        division_ticket = request.json['division_ticket']
        senate_ticket = request.json['senate_ticket']
    else:
        state = request.form['state']
        division = request.form['division']
        division_ticket = request.form['division_ticket'].split(',')
        senate_ticket = request.form['senate_ticket'].split(',')

    ballot_id = store_at_random_id({
        'state': state,
        'division': division,
        'division_ticket': marshal.dumps(division_ticket),
        'senate_ticket': marshal.dumps(senate_ticket),
    })

    return jsonify({'ballot_id': ballot_id})

@app.route('/store/<ballot_id>', methods=['GET'])
def get_ballot(ballot_id):
    r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)

    if not r.exists(ballot_id):
        abort(404)

    ballot = r.hgetall(ballot_id)
    for ticket in ('division_ticket', 'senate_ticket'):
        ballot[ticket] = marshal.loads(ticket)

    return jsonify(ballot)

RESERVED = (
    'act', 'nsw', 'nt', 'qld', 'sa', 'tas', 'vic', 'wa',
    'adelaide', 'aston', 'ballarat', 'banks', 'barker', 'barton', 'bass',
    'batman', 'bendigo', 'bennelong', 'berowra', 'blair', 'blaxland',
    'bonner', 'boothby', 'bowman', 'braddon', 'bradfield', 'brand',
    'brisbane', 'bruce', 'calare', 'calwell', 'canberra', 'canning',
    'capricornia', 'casey', 'charlton', 'chifley', 'chisholm', 'cook',
    'corangamite', 'corio', 'cowan', 'cowper', 'cunningham', 'curtin',
    'dawson', 'deakin', 'denison', 'dickson', 'dobell', 'dunkley', 'durack',
    'edenmonaro', 'fadden', 'fairfax', 'farrer', 'fisher', 'flinders',
    'flynn', 'forde', 'forrest', 'fowler', 'franklin', 'fraser', 'fremantle',
    'gellibrand', 'gilmore', 'gippsland', 'goldstein', 'gorton', 'grayndler',
    'greenway', 'grey', 'griffith', 'groom', 'hasluck', 'herbert', 'higgins',
    'hindmarsh', 'hinkler', 'holt', 'hotham', 'hughes', 'hume', 'hunter',
    'indi', 'isaacs', 'jagajaga', 'kennedy', 'kingsfordsmith', 'kingston',
    'kooyong', 'lalor', 'latrobe', 'leichhardt', 'lilley', 'lindsay',
    'lingiari', 'longman', 'lyne', 'lyons', 'macarthur', 'mackellar',
    'macquarie', 'makin', 'mallee', 'maranoa', 'maribyrnong', 'mayo',
    'mcewen', 'mcmahon', 'mcmillan', 'mcpherson', 'melbourne',
    'melbourneports', 'menzies', 'mitchell', 'moncrieff', 'moore', 'moreton',
    'murray', 'newcastle', 'newengland', 'northsydney', 'oconnor', 'oxley',
    'page', 'parkes', 'parramatta', 'paterson', 'pearce', 'perth', 'petrie',
    'portadelaide', 'rankin', 'reid', 'richmond', 'riverina', 'robertson',
    'ryan', 'scullin', 'shortland', 'solomon', 'stirling', 'sturt', 'swan',
    'sydney', 'tangney', 'throsby', 'wakefield', 'wannon', 'warringah',
    'watson', 'wentworth', 'werriwa', 'widebay', 'wills', 'wright',
)

if __name__ == '__main__':
    app.run(debug=True, port=5005)
