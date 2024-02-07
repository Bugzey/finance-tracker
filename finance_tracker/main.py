"""
Finance tracker main module
"""
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from finance_tracker.qr_handler import (
    get_qr_from_video,
    QRData,
)
from finance_tracker.managers import (
    AccountManager,
    BusinessManager,
    CategoryManager,
    PeriodManager,
    SubcategoryManager,
    TransactionManager,
)
from finance_tracker.models import BaseModel

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(msg)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def interact(prompt: str, choices: list[Any]) -> Any:
    """
    Ask the user a question, provide choices in a menu-like fashion numbering options and return the
    answer corresponding to one of the choices
    """
    print(prompt)
    items = [f"{index+1}: {item}" for index, item in enumerate(choices)]

    print("\n".join(items))
    while True:
        index = input(f"Which path to use? 1-{len(items)}: ")
        if index.isnumeric():
            index = int(index)
            break

        print(f"Invalid input: {index}")

    result = choices[index-1]
    return result


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

        if path and path.exists():
            logger.info(f"Using provided path: {path}")
        elif not path and self.check_standard_paths():
            path = Path(self.check_standard_paths()).expanduser()
            logger.info(f"Using existing standard path: {path}")
        else:
            path = path or self.ask_which_path_to_use()
            logger.info(f"Setting up database: {path}")
            path = Path(path).expanduser()
            self.create_if_not_exists(path)
            self.engine = self.create_engine(path)
            BaseModel.metadata.create_all(self.engine)
            if interact("Use default objects?", ["Yes", "No"]) == "Yes":
                self.initial_setup(engine=self.engine)

        print(f"Using path: {path}")
        self.path = path
        self.engine = self.create_engine(path)

    def check_standard_paths(self):
        return next((item for item in self.paths if item.exists()), None)

    def ask_which_path_to_use(self):
        prompt = "No path provided. Use a standard path?"
        result = interact(prompt, self.paths)
        return result

    def create_if_not_exists(self, path: Path):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        return path

    def create_engine(self, path: Path):
        engine = create_engine(f"sqlite+pysqlite:///{str(path)}")
        return engine

    @staticmethod
    def initial_setup(engine: Engine):
        from finance_tracker.default_data import category, subcategory, account
        _ = [AccountManager(engine).create(**data) for data in account]
        ex_cat = {
            data["name"]: CategoryManager(engine).create(**data).id
            for data
            in category
        }
        [
            SubcategoryManager(engine).create(
                **data, category_id=category_id,
            )
            for item, category_id
            in ex_cat.items()
            for data in subcategory[item]
        ]


def main(args):
    """
    Main method. The args should already be parsed in __main__. They should contain:

    1. action - create, update, delete, get, query
    2. object - what to apply the action to
    """
    logger.setLevel(logging.DEBUG if args.verbose else logging.WARNING)
    db_handler = DBHandler(path=args.database)

    if args.action == "report":
        #   TODO: extract into a separate function
        #   TODO: use conditional imports since finance_tracker[report] might not be
        #   installed
        from threading import Thread
        import webbrowser
        import time
        from finance_tracker.report.app import app

        app.config.engine = db_handler.engine

        def wait_and_open_browser():
            time.sleep(1)
            webbrowser.open("http://localhost:5000")

        _ = Thread(target=wait_and_open_browser).run()
        app.run(debug=args.verbose)
        return

    args.object = (
        args.object[0]
        if isinstance(args.object, list)
        else args.object
    )

    #   Combine data
    args.data = {
        key: value
        for item in args.data
        for key, value
        in item.items()
    }

    match args.object:
        case "account" | "a":
            manager = AccountManager
        case "business" | "b":
            manager = BusinessManager
        case "category" | "c":
            manager = CategoryManager
        case "period" | "p":
            manager = PeriodManager
        case "subcategory" | "s":
            manager = SubcategoryManager
        case "transaction" | "t":
            manager = TransactionManager
        case _:
            raise ValueError(f"Invalid object: {args.object}")

    manager = manager(db_handler.engine)

    match args.action:
        case "help" | "h":
            fields = {
                item.name: item.type
                for item
                in manager.model.__table__.c
                if item.name not in dir(BaseModel)
            }
            print(f"{args.object} possible data: {fields}")
            return
        case "create" | "c":
            if args.qr_code:
                if args.object not in ["business", "b", "transaction", "t"]:
                    raise ValueError(
                        "QR Code flow only available for business and transaction"
                    )
                qrdata = QRData.from_string(get_qr_from_video())
                result = manager.from_qr_code(qrdata, **args.data)
            else:
                result = manager.create(**args.data)
        case "get" | "g":
            result = manager.get(**args.data)
        case "update" | "u":
            result = manager.update(**args.data)
        case "delete" | "d":
            result = manager.delete(**args.data)
        case "query" | "q":
            result = manager.query(args.limit, args.offset, **args.data)
        case _:
            raise ValueError(f"Invalid action: {args.action}")

    print(
        "\n".join(str(item) for item in result)
        if isinstance(result, list)
        else result
    )
    return result
