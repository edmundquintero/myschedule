#!/usr/bin/env python
import logging
from cpsite.management import execute_cpcc_manager
try:
    from myschedule.settings import development 
except ImportError, e:
    import sys
    sys.stderr.write("Error: Can't find the 'development' settings file. Bug Adam about this. Nested error is (%s).\n" % e)
    sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    execute_cpcc_manager(development)
