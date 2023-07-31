"""
Finance tracker main module
"""

from argparse import ArgumentParser, ArgumentError
import shlex
import sys


class HasSubparsers:
    def add_parser(self) -> ArgumentParser:
        pass


class Parser:
    @classmethod
    def make_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(prog="finance_tracker", exit_on_error=False)
        parser.add_argument("-i", "--interactive", action="store_true")
        subparsers = parser.add_subparsers(title="action", dest="action")
        cls._add_category(subparsers)
        cls._add_quit(subparsers)
        return parser

    @classmethod
    def _add_quit(cls, subparsers: HasSubparsers):
        _ = subparsers.add_parser(name="quit")

    @classmethod
    def _add_category(cls, subparsers: HasSubparsers):
        parser = subparsers.add_parser(name="category")
        parser.add_argument("-n", "--name", required=True)


def main():
    parser_maker = Parser()
    parser = parser_maker.make_parser()
    args = parser.parse_args()
    if not args.interactive:
        print(args)
        return

    while True and not args.action == "quit":
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
