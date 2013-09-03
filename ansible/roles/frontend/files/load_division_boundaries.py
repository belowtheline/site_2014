#!/usr/bin/env python

import os
import subprocess
import sys

import pyrax

DATA_FILENAME = 'national-esri-16122011.zip'

sys.path.append('/home/btl/site/api')

import dbcreds

pyrax.set_setting('identity_type', 'rackspace')
pyrax.set_credential_file(os.path.expanduser('~/.raxcreds'), region='SYD')
container = pyrax.cloudfiles.get_container('data')

container.download_object(DATA_FILENAME, '.')
subprocess.check_call(['unzip', DATA_FILENAME])
os.chdir(DATA_FILENAME.rsplit('.')[0])

for filename in os.listdir('.'):
    if filename.endswith('.shp'):
        break

env = dict(os.environ)
env['PGPASSWORD'] = dbcreds.PASSWORD
psql = subprocess.Popen(['/usr/bin/psql', '-h', dbcreds.HOSTNAME, '-U',
                         dbcreds.USERNAME, dbcreds.DATABASE],
                         stdin=subprocess.PIPE, env=env)
subprocess.check_call(['/usr/bin/shp2pgsql', '-s', '4283', '-I', filename],
                       stdout=psql.stdin)

open('/home/btl/divisions-loaded', 'w')