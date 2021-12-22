#!/usr/bin/env python3
#
'''
  Runs a zip file, and shows the log, using the elmerrest API
'''

import os
import sys
from time import sleep, asctime
import threading
import requests

from simplejson.errors import JSONDecodeError
#
def run(file_name):
    '''
      Uploads a zip file, runs it till the end, and downloads the results into a given zip file
    '''
    try:
        with open(file_name, 'rb') as upfile:
            response = requests.post(f'{ELMERRESTURL}/api/v1/cases',
                                     auth=(USER, PASSWD),
                                     files={'upfile': upfile})
        if response.status_code != 200:
            print(f"ERROR ({response.status_code}): {response.url}\n\n{response.text}")
            sys.exit(5)
    except requests.exceptions.ConnectionError as conn_err:
        print(f"\nERROR: Cannot connect to '{ELMERRESTURL}'")
        print("ERROR:", conn_err)
        sys.exit(6)

    try:
        jobid = response.json()["jobid"]
    except JSONDecodeError as jsonerr:
        print(f"ERROR ({response.status_code}): <{ELMERRESTURL}/api/v1/cases> {response.text}")
        print("ERROR: ", jsonerr)
        sys.exit(7)

    status = ""
    while status not in ("done", "failed"):
        response_status = requests.get(f'{ELMERRESTURL}/api/v1/result/{jobid}',
                                       auth=(USER, PASSWD))
        try:
            status = response_status.json()["metadata"]["status"]
        except JSONDecodeError as jsonerr:
            print("ERROR: ", jsonerr)
            print(response_status.text)

        print(f"{asctime()} [{jobid}] Status: {status}")
        sleep(5)

    local_filename = f'./results-{jobid}.zip'

    print(f"{asctime()} [{jobid}] Downloading {local_filename}")
    with requests.get(f'{ELMERRESTURL}/api/v1/result/{jobid}/file',
                      auth=(USER, PASSWD),
                      stream=True) as res:
        try:
            res.raise_for_status()
            with open(local_filename, 'wb') as dff:
                for chunk in res.iter_content(chunk_size=8192):
                    dff.write(chunk)
        except requests.exceptions.HTTPError as httperr:
            print(f"ERROR: {httperr}")
    print(f"{asctime()} [{jobid}] DONE")
#
def log(job_id):
    '''
      Return the log of a given jobid
    '''
    response_status = requests.get(f'{ELMERRESTURL}/api/v1/result/{job_id}',
                                   auth=(USER, PASSWD))
    if response_status.status_code != '200':
        print(f"ERROR: ({response_status.status_code})")
    try:
        print(response_status.json()['metadata']['logs'])
    except JSONDecodeError as json_err:
        print("ERROR:", json_err)
        sys.exit(8)

def list_job():
    '''
        List all cases
    '''
    response_status = requests.get(f'{ELMERRESTURL}/api/v1/job/',
                                   auth=(USER, PASSWD))
    try:
        for case in response_status.json():
            print(case)
    except JSONDecodeError:
        print("ERROR: ", response_status.text)
#####

HELP_STRING = f"""Use:
{sys.argv[0]}
        run <Zip file>
        log <jobid>
        list"""

try:
    VERB = sys.argv[1]
except IndexError:
    print(HELP_STRING)
    sys.exit(1)

try:
    USER = os.environ['ELMERRESTUSER']
except KeyError:
    USER = 'elmeruser'

try:
    ELMERRESTURL = os.environ['ELMERRESTURL']
except KeyError:
    ELMERRESTURL = 'https://ahtools-devel.rahtiapp.fi'
#
print(f"Using:\n    * USER: '{USER}'\n    * ELMERRESTURL: '{ELMERRESTURL}'.")
print("You may use the environment varibles $ELMERRESTUSER and $ELMERRESTURL to change that")
#
DIRNAME = os.path.dirname(__file__)

print("---")

try:
    print(f"Reading password from {DIRNAME}/passwd")
    with open(f'{DIRNAME}/passwd', 'r', encoding="utf8") as pf:
        PASSWD = pf.read().rstrip()
except FileNotFoundError:
    print(f"Cannot find '{DIRNAME}/passwd' file")
    sys.exit(2)
#

try:
    if VERB == 'run':
        THREADS = []
        for job in sys.argv[2:]:
            x = threading.Thread(target=run, args=(job,))
            THREADS.append(x)
            x.start()
        for index, thread in enumerate(THREADS):
            thread.join()

    elif VERB == 'log':
        log(sys.argv[2])
    elif VERB == 'list':
        list_job()
    else:
        print(HELP_STRING)
        sys.exit(3)
except IndexError:
    print(HELP_STRING)
    sys.exit(4)
#
