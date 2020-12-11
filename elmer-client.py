#!/usr/bin/env python3
#
'''
  Runs a zip file, and shows the log, using the elmerrest API
'''

import os
import sys
from time import sleep, asctime
import requests

from simplejson.errors import JSONDecodeError
#
def run(file_name):
    '''
      Uploads a zip file, runs it till the end, and downloads the results into a given zip file
    '''
    response = requests.post('%s/api/v1/cases' % BASE_URL,
                             auth=(USER, PASSWD),
                             files={'upfile': open(file_name, 'rb')})
    if response.status_code != 200:
        print("ERROR (%d): %s %s" % (response.status_code, BASE_URL, response.text))
        sys.exit(3)

    jobid = response.json()["jobid"]

    status = ""
    while status not in ("done", "failed"):
        response_status = requests.get('%s/api/v1/result/%s' % (BASE_URL, jobid),
                                       auth=(USER, PASSWD))
        try:
            status = response_status.json()["metadata"]["status"]
        except JSONDecodeError as jsonerr:
            print("ERROR: ", jsonerr)
            print(response_status.text)

        print("%s [%s] Status: %s" % (asctime(), jobid, status))
        sleep(5)

    local_filename = './results-%s.zip' % jobid

    print("Downloading %s" % local_filename)
    with requests.get('%s/api/v1/result/%s/file' % (BASE_URL, jobid),
                      auth=(USER, PASSWD),
                      stream=True) as res:
        res.raise_for_status()
        with open(local_filename, 'wb') as dff:
            for chunk in res.iter_content(chunk_size=8192):
                dff.write(chunk)
    print("DONE")
#
def log(job_id):
    '''
      Return the log of a given jobid
    '''
    response_status = requests.get('%s/api/v1/result/%s' % (BASE_URL, job_id), auth=(USER, PASSWD))
    try:
        print(response_status.json()['metadata']['logs'])
    except JSONDecodeError:
        print("ERROR: ", response_status.text)
#####

HELP_STRING = """Use:
%s
        run <Zip file>
        log <jobid>""" % sys.argv[0]

try:
    VERB = sys.argv[1]
except IndexError:
    print(HELP_STRING)
    sys.exit(2)

try:
    USER = os.environ['ELMERRESTUSER']
except KeyError:
    USER = 'elmeruser'

try:
    BASE_URL = os.environ['ELMERRESTURL']
except KeyError:
    BASE_URL = 'https://elmerrest-devel.rahtiapp.fi'
#
print("Using:\n    * USER: '%s'\n    * BASE_URL: '%s'." % (USER, BASE_URL))
print("You may use the environment varibles $ELMERRESTUSER and $ELMERRESTURL to change that")
#
DIRNAME = os.path.dirname(__file__)

print("---")

try:
    print("Reading password from %s/passwd" % DIRNAME)
    with open('%s/passwd' % DIRNAME, 'r') as pf:
        PASSWD = pf.read().rstrip()
except FileNotFoundError:
    print("Cannot find '%s/passwd' file" % DIRNAME)
    sys.exit(1)
#

try:
    if VERB == 'run':
        run(sys.argv[2])
    elif VERB == 'log':
        log(sys.argv[2])
    else:
        print(HELP_STRING)
        sys.exit(3)
except IndexError:
    print(HELP_STRING)
    sys.exit(2)
#
