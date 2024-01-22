from processes import Processes
import pprint

Procs = Processes('./Processes')
pprint.pprint(Procs.glob_files('*'))


pprint.pprint(Procs['Snake6/2- Make Server Implementation Plan'])
