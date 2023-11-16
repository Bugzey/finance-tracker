"""
Finance tracker main module
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from finance_tracker.managers import (
    AccountManager,
    BusinessManager,
    CategoryManager,
    PeriodManager,
    SubcategoryManager,
    TransactionManager,
)
from finance_tracker.models import BaseModel


class DBHandler:
    engine: Engine
    path: Path

    paths = (
        Path("~/.config/finance_tracker/finance_tracker.db").expanduser(),
        Path("~/.finance_tracker.db").expanduser(),
        Path("./finance_tracker.db").expanduser(),
    )

    def __init__(self, path: Path = None):
        if path:
            path = Path(path).expanduser()
            assert path.exists(), "Given path not found"
            self.path = path
            return

        #   Check for standard paths
        print("No path provided. Use a standard path?")
        path = self.check_standard()
        path = self.create_if_not_exists(path)
        self.path = path
        self.engine = self.create_engine(path)
        BaseModel.metadata.create_all(self.engine)

    def check_standard(self):
        prompt = []
        for index, path in enumerate(self.paths):
            if path.exists():
                prompt.append(f"{index+1}: {path}: FOUND")
            else:
                prompt.append(f"{index+1}: {path}: missing")

        print("\n".join(prompt))
        while True:
            index = input(f"Which path to use? 1-{len(self.paths)}: ")
            if index.isnumeric():
                index = int(index)
                break

            print(f"Invalid input: {index}")

        result = self.paths[index-1]
        return result

    def create_if_not_exists(self, path: Path):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        return path

    def create_engine(self, path: Path):
        engine = create_engine(f"sqlite+pysqlite:///{str(path)}")
        return engine


def main(args):
    """
    Main method. The args should already be parsed in __main__. They should contain:

    1. action - create, update, delete, get, query
    2. object - what to apply the action to
    """
    db_handler = DBHandler(path=args.database)
    args.object = (
        args.object[0]
        if isinstance(args.object, list)
        else args.object
    )

    match args.object:
        case "account":
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

    manager = manager(db_handler.engine)

    match args.action:
        case "help":
            fields = {
                item.name: item.type
                for item
                in manager.model.__table__.c
                if item.name not in dir(BaseModel)
            }
            print(f"{args.object} possible data: {fields}")
            return
        case "create":
            result = manager.create(**args.data)
        case "get":
            result = manager.get(**args.data)
        case "update":
            result = manager.update(**args.data)
        case "delete":
            result = manager.delete(**args.data)
        case "query":
            result = manager.query(**args.data)
        case _:
            raise ValueError(f"Invalid action: {args.action}")

    print(result)
    return result
