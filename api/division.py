#!/usr/bin/env python

from datetime import timedelta
from functools import update_wrapper

from flask import Flask, abort, current_app, jsonify, make_response, request

import psycopg2

import dbcreds

QUERY_FORMAT = """
SELECT elect_div FROM com20111216_elb_region WHERE
    ST_Contains(geom, ST_SetSRID(ST_Point({longitude:f}, {latitude:f}), 4283))
"""

app = Flask(__name__)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('/home/benno/logs/division.log')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

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

@app.route('/division', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'X-Requested-With'])
def division_lookup():
    if request.json is None and request.method == 'POST':
        abort(400, "Must provide JSON (did you set Content-type?)")
    elif request.method == 'POST':
        args = request.json
    else:
        args = request.args

    if 'latitude' not in args:
        abort(400, "Most provide latitude and longitude")
    if 'longitude' not in args:
        abort(400, "Most provide latitude and longitude")

    conn = psycopg2.connect(host=dbcreds.HOSTNAME, database=dbcreds.DATABASE,
                            user=dbcreds.USERNAME, password=dbcreds.PASSWORD)
    cursor = conn.cursor()

    cursor.execute(QUERY_FORMAT.format(latitude=float(args['latitude']),
                                       longitude=float(args['longitude'])))

    result = cursor.fetchone()
    if result is None:
        name = None
    else:
        name = result[0].lower().translate(None, " -'")
    return jsonify({'division': name})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
