def run_test():
    logging.basicConfig(level = logging.INFO)
    logging.info("Creating database instance")
    test_db = Database()

    logging.info("Insert dummy categories")
    test_db.add_category("bla")
    test_db.add_category(["bla1", "bla2"])

    logging.info("Insert dummy subcategories")
    test_db.add_subcategory("sub_bla", "bla")
    test_db.add_subcategory(["sub_bla1", "sub_bla2"], "bla")

    logging.info("Printing results")
    logging.info(list(test_db.list_categories()))
    logging.info(list(test_db.list_subcategories("bla")))


if __name__ == "__main__":
    run_test()
