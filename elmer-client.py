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
    try:
        response = requests.post('%s/api/v1/cases' % ELMERRESTURL,
                                 auth=(USER, PASSWD),
                                 files={'upfile': open(file_name, 'rb')})
        if response.status_code != 200:
            print("ERROR (%d): %s\n\n%s" % (response.status_code, response.url, response.text))
            sys.exit(3)
    except requests.exceptions.ConnectionError as conn_err:
        print(conn_err)
        sys.exit(5)

    try:
        jobid = response.json()["jobid"]
    except JSONDecodeError as jsonerr:
        print("ERROR (%d): <%s/api/v1/cases> %s" % (response.status_code,
                                                    ELMERRESTURL, response.text))
        print(jsonerr)
        sys.exit(4)

    status = ""
    while status not in ("done", "failed"):
        response_status = requests.get('%s/api/v1/result/%s' % (ELMERRESTURL, jobid),
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
    with requests.get('%s/api/v1/result/%s/file' % (ELMERRESTURL, jobid),
                      auth=(USER, PASSWD),
                      stream=True) as res:
        try:
            res.raise_for_status()
            with open(local_filename, 'wb') as dff:
                for chunk in res.iter_content(chunk_size=8192):
                    dff.write(chunk)
        except requests.exceptions.HTTPError as httperr:
            print("ERROR: %s" % httperr)
    print("DONE")
#
def log(job_id):
    '''
      Return the log of a given jobid
    '''
    response_status = requests.get('%s/api/v1/result/%s' % (ELMERRESTURL, job_id),
                                   auth=(USER, PASSWD))
    try:
        print(response_status.json()['metadata']['logs'])
    except JSONDecodeError:
        print("ERROR: ", response_status.text)

def list():
    '''
        List all cases
    '''
    response_status = requests.get('%s/api/v1/job/' % (ELMERRESTURL),
                                   auth=(USER, PASSWD))
    try:
        for case in response_status.json():
            print(case)
    except JSONDecodeError:
        print("ERROR: ", response_status.text)

#####

HELP_STRING = """Use:
%s
        run <Zip file>
        log <jobid>
        list""" % sys.argv[0]

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
    ELMERRESTURL = os.environ['ELMERRESTURL']
except KeyError:
    ELMERRESTURL = 'https://ahtools-devel.rahtiapp.fi'
#
print("Using:\n    * USER: '%s'\n    * ELMERRESTURL: '%s'." % (USER, ELMERRESTURL))
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
    elif VERB == 'list':
        list()
    else:
        print(HELP_STRING)
        sys.exit(3)
except IndexError:
    print(HELP_STRING)
    sys.exit(2)
#
