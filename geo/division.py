#!/usr/bin/env python

from flask import Flask, abort, request
from flask.ext.restful import Api, Resource

import psycopg2

HOSTNAME = "localhost"
DATABASE = "btl"
USERNAME = "btl"
PASSWORD = "JWHgamq9fCWe6vjhgrJL"

QUERY_FORMAT = """
SELECT elect_div FROM com20111216_elb_region WHERE
    ST_Contains(geom, ST_SetSRID(ST_Point({longitude:f}, {latitude:f}), 4283))
"""

app = Flask(__name__)
api = Api(app)

class DivisionLookup(Resource):
    def post(self):
        if request.json is None:
            abort(400, "Must provide JSON (did you set Content-type?)")
        if 'latitude' not in request.json:
            abort(400, "Most provide latitude and longitude")
        if 'longitude' not in request.json:
            abort(400, "Most provide latitude and longitude")

        conn = psycopg2.connect(host=HOSTNAME, database=DATABASE,
                                user=USERNAME, password=PASSWORD)
        cursor = conn.cursor()

        cursor.execute(QUERY_FORMAT.format(latitude=request.json['latitude'],
                                           longitude=request.json['longitude']))

        result = cursor.fetchone()
        if result is None:
            return {'division': None}
        name = result[0].lower().strip(" -'")
        return {'division': name}

api.add_resource(DivisionLookup, '/division')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
