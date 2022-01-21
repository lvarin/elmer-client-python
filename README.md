# ELMERREST client

This is a client for the ELMER REST API. It csn be used as a fast way to submit jobs, or as an example to integrate ELMERREST API in a bigger project.
it has three options `run`, `log` and `list`:

```sh
$ ./elmer_client.py
Use:
 ./elmer_client.py
        run <Zip file>
        log <jobid>
        list
```

## Install dependencies

This client requires only two dependencies: `requests` to make the HTTP requests to the API, and `simplejson` to process the JSON returned by the API. In order to install the dependencies run:

```
pip install -r requirements.txt
```

## elmer_client.py run

This command receives a zip file, runs it showing the status every 5 seconds, and then downloads the results. For example:

```sh
$ vim passwd # add the password there
$ zip case.zip */* *;
  adding: case.sif (deflated 53%)
  adding: ComplexMode.f90 (deflated 78%)
  adding: ELMERSOLVER_STARTINFO (stored 0%)
  adding: job.sh (deflated 61%)
  adding: params_sif.txt (deflated 3%)
  adding: stator3d/ (stored 0%)
  adding: stator_material_sif.txt (deflated 83%)
$ ./elmer-client.py run case.zip
Using:
    * USER: 'elmeruser'
    * ELMERRESTURL: 'https://elmerrest-devel.rahtiapp.fi'.
You may use the environment varibles $ELMERRESTUSER and $ELMERRESTURL to change that
---
Reading password from ./passwd
Fri Dec 11 16:34:53 2020 [case-1607697292] Status: submitted
Fri Dec 11 16:34:58 2020 [case-1607697292] Status: active
Fri Dec 11 16:35:03 2020 [case-1607697292] Status: active
Fri Dec 11 16:35:08 2020 [case-1607697292] Status: active
(...)
Fri Dec 11 16:37:48 2020 [case-1607697292] Status: active
Fri Dec 11 16:37:54 2020 [case-1607697292] Status: done
Downloading ./results-case-1607697292.zip
DONE
```

## elmer_client.py log

```sh
$ ./elmer_client.py log case-1607697292 | head -n 25
Using:
    * USER: 'elmeruser'
    * ELMERRESTURL: 'https://elmerrest-devel.rahtiapp.fi'.
You may use the environment varibles $ELMERRESTUSER and $ELMERRESTURL to change that
---
Reading password from ./passwd
+ cd //elmer-cases/input/case/
+ ./job.sh
+ tee case.log

Starting program Elmergrid
Elmergrid reading in-line arguments
Using dual (elemental) graph in partitioning.
The mesh will be partitioned with Metis to 2 partitions.
Output will be saved to file stator3d.

Elmergrid loading data:
-----------------------
Loading mesh in ElmerSolver format from directory stator3d.
Loading header from mesh.header
Maximum elementtype index is: 706
Maximum number of nodes in element is: 6
Allocating for 3960 knots and 5850 elements.
Loading 3960 Elmer nodes from mesh.nodes
Loading 5850 bulk elements from mesh.elements
```

## elmer_client.py list

```
$ ./elmer_client.py list
Using:
    * USER: 'elmeruser'
    * ELMERRESTURL: 'https://ahtools-devel.rahtiapp.fi'.
You may use the environment varibles $ELMERRESTUSER and $ELMERRESTURL to change that
---
Reading password from ./passwd
statoreigenmode-1633951725
statoreigenmode-1633951729
statoreigenmode-1633953267
statoreigenmode-1633955245
statoreigenmode-1633957518
statoreigenmode-1639114711
```

