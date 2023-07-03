"""
Finance tracker main module
"""

from argparse import ArgumentParser, ArgumentError
import shlex
import sys


class Parser:
    def __init__(self):
        self.parser = ArgumentParser(prog="finance_tracker", exit_on_error=False)
        self.parser.add_argument("-i", "--interactive", action="store_true")
        self.subparsers = self.parser.add_subparsers(title="action", dest="action")
        self._add_category()
        self._add_quit()

    def _add_quit(self):
        parser = self.subparsers.add_parser(name="quit")

    def _add_category(self):
        parser = self.subparsers.add_parser(name="category")
        parser.add_argument("-n", "--name", required=True)


def main():
    parser = Parser().parser
    args = parser.parse_args()
    if not args.interactive:
        pring(args)
        return

    while True and not args.action=="quit":
        try:
            args = parser.parse_args(shlex.split(input()))
        except SystemExit:
            print(parser.format_usage())
            continue
        except KeyboardInterrupt:
            sys.exit()
        except EOFError:
            sys.exit()

        print(args)
