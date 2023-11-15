"""
Finance tracker main module
"""

from finance_tracker.managers import (
    AccountManager,
    BusinessManager,
    CategoryManager,
    PeriodManager,
    SubcategoryManager,
    TransactionManager,
)


def main(args):
    """
    Main method. The args should already be parsed in __main__. They should contain:

    1. action - create, update, delete, get, query
    2. object - what to apply the action to
    """
    match args.object:
        case "accont":
            manager = AccountManager
        case "business":
            manager = BusinessManager
        case "category":
            manager = CategoryManager
        case "period":
            manager = PeriodManager
        case "subcategory":
            manager = SubcategoryManager
        case "transaction":
            manager = TransactionManager
        case _:
            raise ValueError(f"Invalid object: {args.object}")

    data = process_data(args.data)

    match args.action:
        case "create":
            result = manager.create(**data)
