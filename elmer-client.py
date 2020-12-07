#!/usr/bin/env python3
#
import requests
import os
import sys
from time import sleep, asctime
#
user='elmeruser'
baseURL='https://elmerrest-devel.rahtiapp.fi'
#
dirname=os.path.dirname(__file__)

try:
  with open('%s/passwd' % dirname, 'r') as f:
    passwd = f.read().rstrip()
except FileNotFoundError:
  print("Cannot find 'passwd' file")
  exit(0)
#
try:
  fileName=sys.argv[1]
except IndexError:
  print('Use: %s <Zip file>' % sys.argv[0])
  exit(1)
#
#
response = requests.post('%s/api/v1/cases' % baseURL, auth=(user, passwd), files={'upfile': open(fileName,'rb')})
if response.status_code != 200:
  print("ERROR (%d): %s" % (response.status_code, response.text))
  exit(2)

jobid = response.json()["jobid"]

status = ""
while status != "done" and status != "failed":
  response_status = requests.get('%s/api/v1/result/%s' % (baseURL, jobid), auth=(user, passwd))
  status = response_status.json()["metadata"]["status"]
  print("%s [%s] Status: %s" % (asctime(), jobid, status))
  sleep(5)

#print(response_status.json())

local_filename = './results-%s.zip' % jobid

print("Downloading %s" % local_filename)
with requests.get('%s/api/v1/result/%s/file' % (baseURL, jobid), auth=(user, passwd), stream=True) as r:
  r.raise_for_status()
  with open(local_filename, 'wb') as f:
    for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


