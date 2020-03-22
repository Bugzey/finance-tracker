"""Functions to interface with an SQLite database

"""

import sqlite3
import os
import logging
import pkgutil

class Database:
    def __init__(self, file_path = ":memory:"):
        self.file_path = file_path
        self._con = sqlite3.connect(file_path)

        if file_path == ":memory:" or not os.path.exists(file_path):
            logging.info("Database not found, generating schema")
            self.create_database()

    def create_database(self):
        schema = pkgutil.get_data(__package__, "schema.sql") # get file within the defined package
        self._con.executescript(schema.decode("utf-8"))


    def add_category(self, category_name):
        insert_query = """
        insert into category (
                historic_category_name
                , current_category_name
        )
        values
                (:category_name, :category_name);
        """
        current_categories_query = "select current_category_name from category where valid_to_time is null"
        current_categories = self._con.execute(current_categories_query)

        #   Allow bulk execution
        if type(category_name) in [int, float, str]:
            assert category_name not in current_categories, f"Categories already exist: {category_name}"
            self._con.execute(insert_query, {"category_name": category_name})
        elif type(category_name) == list:
            assert not any(map(lambda x: x in current_categories, category_name)), f"Categories already exist: {', '.join(category_name)}"
            args = ({"category_name": item} for item in category_name)
            self._con.executemany(insert_query, args)
        else:
            raise TypeError(f"Unsupported table name type: {type(category_name)}")


    def add_subcategory(self, subcategory_name, category_name):
        get_category_id = """
        select category_id 
        from category
        where current_category_name = ?
        and valid_to_time is null
        ;
        """
        get_current_subcategories = """
        select current_subcategory_name
        from subcategory
        where category_id = ?
        and valid_to_time is null
        """
        insert_query = """
        insert into subcategory (
            category_id
            , current_subcategory_name
            , historic_subcategory_name
        )
        values
            (:category_id, :subcategory_name, :subcategory_name)
        ;
        """
        category_id = next(self._con.execute(get_category_id, [category_name]))
        current_subcategories = self._con.execute(get_current_subcategories, category_id)

        if type(subcategory_name) in [str, int, float]:
            assert subcategory_name not in current_subcategories, f"Subcategories already exist: {subcategory_name}"
            self._con.execute(insert_query, {"category_id": category_id[0], "subcategory_name": subcategory_name})
        elif type(subcategory_name) == list:
            assert not any(map(lambda x: x in current_subcategories, subcategory_name)), f"Subcategories already exist: {', '.join(subcategory_name)}"
            args = ({"category_id": category_id[0], "subcategory_name": item} for item in subcategory_name)
            self._con.executemany(insert_query, args)
        else:
            raise TypeError(f"Unsupported table name type: {type(subcategory_name)}")


    def modify_category():
        pass

    def modify_subcategory():
        pass

    def read_balance():
        pass

    def write_balance():
        pass

    def read_transaction():
        pass

    def write_transaction():
        pass

    def list_categories(self):
        query = "select cat.* from category cat"
        result = self._con.execute(query)
        return(result)

    def list_subcategories(self, category):
        query = """
        select 
            sub.* 
        from
            subcategory sub
            join category cat
            on sub.category_id = cat.category_id
        where 
            cat.current_category_name = :category
        ;
        """
        result = self._con.execute(query, [category])
        return(result)


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
