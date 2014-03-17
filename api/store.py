from datetime import timedelta
from functools import update_wrapper

import functools
import os
import random
import string

from flask import Flask, abort, current_app, jsonify, make_response, redirect, \
                  request
import redis
import rollbar

ID_ALPHABET = ''.join([string.lowercase, string.uppercase, string.digits])
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = int(os.environ.get('REDIS_DB', 5))
MAX_TRIES = 10

app = Flask(__name__)

def setup_rollbar(environment):
    if 'ROLLBAR_TOKEN' not in os.environ:
        return
    rollbar.init(os.environ['ROLLBAR_TOKEN'], environment,
                 allow_logging_basic_config=False)

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

def store_at_random_id(ballot, start_length=8):
    r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)
    candidate = None
    n = start_length
    tries = 0

    def store(c):
        if c is None:
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
@crossdomain(origin=['*'], headers=['Content-Type', 'X-Requested-With'])
def store_ballot():
    try:
        if request.json is not None:
            state = request.json['state']
            state_only = request.json['state_only']
            if not state_only:
                division = request.json['division']
                division_ticket = request.json['division_ticket']
            else:
                division = None
                division_ticket = None
            senate_ticket = request.json['senate_ticket']
            order_by_group = request.json['order_by_group']
        else:
            state = request.form['state']
            state_only = int(request.form['state_only'])
            if not state_only:
                division = request.form['division']
                division_ticket = request.form['division_ticket'].split(',')
            else:
                division = None
                division_ticket = None
            senate_ticket = request.form['senate_ticket'].split(',')
            order_by_group = bool(int(request.form['order_by_group']))

        if state_only:
            state_only = 1
        else:
            state_only = 0

        ballot = {
            'state': state,
            'state_only': state_only,
            'senate_ticket': ','.join(str(x) for x in senate_ticket),
            'order_by_group': int(order_by_group),
        }

        if not state_only:
            ballot['division'] = division
            ballot['division_ticket'] = ','.join(str(x) for x in division_ticket)

        ballot_id = store_at_random_id(ballot)

        return jsonify({'ballot_id': ballot_id})
    except:
        rollbar.report_exc_info()
        raise

@app.route('/b/<ballot_id>')
@crossdomain(origin=['*'], headers=['Content-Type', 'X-Requested-With'])
def redirect_ballot(ballot_id):
    try:
        r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)

        if not r.exists(ballot_id):
            abort(404)

        division = r.hget(ballot_id, 'division')
        url = 'http://belowtheline.org.au/editor/{}#{}'.format(division, ballot_id)
        return redirect(url)
    except:
        rollbar.report_exc_info()
        raise

@app.route('/store/<ballot_id>', methods=['GET', 'OPTIONS'])
@crossdomain(origin=['*'], headers=['Content-Type', 'X-Requested-With'])
def get_ballot(ballot_id):
    try:
        r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)

        if not r.exists(ballot_id):
            abort(404)

        ballot = r.hgetall(ballot_id)
        ballot['state_only'] = bool(int(ballot.get('state_only', 0)))
        ballot['order_by_group'] = bool(int(ballot['order_by_group']))
        ballot['senate_ticket'] = \
            [int(x) for x in ballot['senate_ticket'].split(',')]
        if not ballot['state_only']:
            ballot['division_ticket'] = \
                [int(x) for x in ballot['division_ticket'].split(',')]

        return jsonify(ballot)
    except:
        rollbar.report_exc_info()
        raise

if __name__ == '__main__':
    setup_rollbar('debug')
    app.run(debug=True, port=5005)
else:
    setup_rollbar('production')

