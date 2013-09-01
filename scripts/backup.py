#!/usr/bin/env python

import datetime
import gzip
import json
import os

import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = int(os.environ.get('REDIS_DB', 5))

r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)

timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
filename = 'backup-{}.json.gz'.format(timestamp)
backup = gzip.GzipFile(filename, 'w', 9)
backup.write('{"backup":[')

keys = r.keys('*')
while keys:
    key = keys.pop()
    record = r.hgetall(key)
    record['id'] = key
    backup.write(json.dumps(record))
    if keys:
        backup.write(',')

backup.write(']}')
backup.close()

container = pyrax.cloudfiles.get_container('backups')
container.upload_file(filename)
