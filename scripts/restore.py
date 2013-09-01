#!/usr/bin/env python

import argparse
import gzip
import json
import os
import os.path

import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = int(os.environ.get('REDIS_DB', 5))

parser = argparse.ArgumentParser()
parser.add_argument('which', nargs='?', default=None)
args = parser.parse_args()

if args.which is None:
    print "Finding latest backup..."

    import pyrax
    pyrax.set_setting('identity_type', 'rackspace')
    pyrax.set_credential_file(os.path.expanduser('~/.raxcreds'), region='SYD')
    container = pyrax.cloudfiles.get_container('backups')

    backups = container.get_objects()
    backups.sort(key=lambda x: x.name)
    print "Downloading {}...".format(backups[-1].name)
    container.download_object(backups[-1].name, '.')
    backup = backups[-1].name
else:
    backup = args.which

r = redis.StrictRedis(host=REDIS_HOST, db=REDIS_DB)

for entry in json.loads(gzip.GzipFile(backup, 'r').read())['backup']:
    key = entry.pop('id')
    p = r.pipeline()
    for k, v in entry.items():
        p.hset(key, k, v)
    p.execute()
