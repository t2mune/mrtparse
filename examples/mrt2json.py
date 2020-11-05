#!/usr/bin/python

import json
import sys
from mrtparse import *

def main():
    """
    Main entry point.

    Args:
    """
    sys.stdout.write('[\n')
    i = 0
    for entry in Reader(sys.argv[1]):
        if i != 0:
            sys.stdout.write(',\n')
        sys.stdout.write(json.dumps([entry.data], indent=2)[2:-2])
        i += 1
    sys.stdout.write('\n]\n')

if __name__ == '__main__':
    main()
