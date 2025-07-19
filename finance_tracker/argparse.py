"""
Module with argument parsing
"""
from argparse import ArgumentParser
from itertools import chain


class HasSubparsers:
    def add_parser(*args, **kwargs):
        pass


def process_data(data: str):
    """
    Process a single data item - items are already split
    """
    key, value = data.split("=", 1)
    return {key: value}


class Parser:
    objects = (
        "transaction",
        "category",
        "subcategory",
        "account",
        "business",
        "period",
    )

    def get_parser(self):
        parser = ArgumentParser(prog="finance_tracker")
        parser.add_argument(
            "-d",
            "--database",
            help="Path to database file",
        )
        parser.add_argument("-v", "--verbose", help="Print verbose messages", action="store_true")

        subparsers = parser.add_subparsers(dest="action", required=True)
        c1 = self.add_action(subparsers, "create", "Create an item")
        c2 = self.add_action(subparsers, "c", "Create an item")
        _ = self.add_action(subparsers, "update", "Update an item")
        _ = self.add_action(subparsers, "u", "Update an item")
        _ = self.add_action(subparsers, "delete", "Delete an item")
        _ = self.add_action(subparsers, "d", "Delete an item")
        _ = self.add_action(subparsers, "get", "Get an item")
        _ = self.add_action(subparsers, "g", "Get an item")
        q1 = self.add_action(subparsers, "query", "Query for items")
        q2 = self.add_action(subparsers, "q", "Query for items")
        _ = self.add_action(subparsers, "help", "Get a list of data items")
        _ = self.add_action(subparsers, "h", "Get a list of data items")

        _ = subparsers.add_parser("report", help="Run report server")

        #   Add bonus options
        c1.add_argument("-q", "--qr-code", help="Create from QR code", action="store_true")
        c2.add_argument("-q", "--qr-code", help="Create from QR code", action="store_true")
        q1.add_argument("-l", "--limit", help="How many rows to return", type=int, default=100)
        q2.add_argument("-l", "--limit", help="How many rows to return", type=int, default=100)
        q1.add_argument("-o", "--offset", help="How many rows to offset", type=int, default=0)
        q2.add_argument("-o", "--offset", help="How many rows to offset", type=int, default=0)
        return parser

    @classmethod
    def add_objects_argument(cls, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(
            "object",
            choices=list(chain(*[[item, item[0]]for item in cls.objects])),
            nargs=1,
        )
        return parser

    @classmethod
    def add_action(
        cls,
        subparsers: HasSubparsers,
        action: str,
        help: str,
    ) -> ArgumentParser:
        parser = subparsers.add_parser(name=action)
        parser = cls.add_objects_argument(parser)
        _ = parser.add_argument(
            "data",
            help="Key-value pairs in the form KEY=VALUE",
            nargs="*",
            type=process_data,
            default={},
        )
        return parser
