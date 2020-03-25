import logging
from finance_tracker.database.database import *

def run_test():
    logging.basicConfig(level = logging.DEBUG)
    logging.info("Creating database instance")
    test_db = Database()

    logging.info("Insert dummy categories")
    test_db.add_category("bla")
    test_db.add_category(["bla1", "bla2"])

    logging.info("Insert dummy subcategories")
    test_db.add_subcategory("sub_bla", "bla")
    test_db.add_subcategory(["sub_bla1", "sub_bla2"], "bla")

    logging.info("Get dummy category id")
    test_category_id = test_db.get_category("bla")
    logging.info(test_category_id)

    logging.info("Get dummy subcategories")
    test_subcategory_id = test_db.get_subcategory(test_category_id[0])
    logging.info(test_subcategory_id)

    logging.info("Print everything")
    logging.info(list(test_db.list_categories()))
    logging.info(list(test_db.list_subcategories("bla")))


if __name__ == "__main__":
    run_test()
