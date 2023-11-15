from argparse import ArgumentParser


class HasSubparsers:
    def add_parser(*args, **kwargs):
        pass


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
        subparsers = parser.add_subparsers(dest="action")
        _ = self.add_action(subparsers, "create", "Create an item")
        _ = self.add_action(subparsers, "c", "Create an item")
        _ = self.add_action(subparsers, "update", "Update an item")
        _ = self.add_action(subparsers, "u", "Update an item")
        _ = self.add_action(subparsers, "delete", "Delete an item")
        _ = self.add_action(subparsers, "d", "Delete an item")
        _ = self.add_action(subparsers, "get", "Get an item")
        _ = self.add_action(subparsers, "g", "Get an item")
        _ = self.add_action(subparsers, "query", "Query for items")
        _ = self.add_action(subparsers, "q", "Query for items")
        return parser

    @classmethod
    def add_objects_argument(cls, parser: ArgumentParser):
        parser.add_argument(
            "object",
            choices=[
                *cls.objects, *[item[0] for item in cls.objects],
            ],
        )
        return parser

    @classmethod
    def add_action(
        cls,
        subparsers: HasSubparsers,
        action: str,
        help: str,
    ):
        parser = subparsers.add_parser(name=action)
        parser = cls.add_objects_argument(parser)
        return parser
