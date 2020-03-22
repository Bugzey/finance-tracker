#!/usr/bin/python
"""Finance Tracker

Call functions, set up database, handle CLI input, orchestrate import/export

Usage:
    finance-tracker [options] list (balance | transaction | category | subcategory)
    finance-tracker [options] add (balance | transaction) <amount>
    finance-tracker [options] modify (balance | transaction) <amount>
    finance-tracker [options] void (balance | transaction) <amount>

Options:
    -a, --accounting-date DATE  Accounting date 
    -t, --transaction-date DATE  Transaction date
    -c, --category=CATEGORY  Item category
    -s, --subcategory=SUBCATEGORY  Item subcateogry
    -d, --database=PATH  Path to the database
    -h, --help  Show this screen
    -v, --version   Display version information
"""

import sys
import os
from docopt import docopt

def get_args():
    argv = sys.argv[1:]
    args = docopt(__doc__, argv = argv)
    print(args)

def print_help():
    print(__doc__)

def main():
    print_help()
    get_args()
    sys.exit(0)

if __name__ == "__main__":
    main()
