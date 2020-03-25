"""Functions to interface with an SQLite database

"""

import sqlite3
import os
import logging
import pkgutil

logger = logging.getLogger(__name__)

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

    
    def get_category(self, name):
        query = """
        select 
            category_id 
            , current_category_name
        from category
        where current_category_name = :name
        and valid_to_time is null
        ;
        """
        if type(name) in [str, int, float]:
            category_id = self._con.execute(query, {"name": name}).fetchone()
        elif type(name) == list:
            category_id = self._con.executemany(query, [{"name": item} for item in name]).fetchall()

        return(category_id)


    def get_subcategory(self, category_id):
        query = """
        select 
            subcategory_id
            , category_id
            , current_subcategory_name
        from subcategory
        where category_id = :category_id
        and valid_to_time is null
        """
        subcategory_id = self._con.execute(query, {"category_id": category_id}).fetchall()
        return(subcategory_id)


    def add_category(self, category_name):
        insert_query = """
        insert into category (
                historic_category_name
                , current_category_name
        )
        values
                (:category_name, :category_name);
        """
        current_categories = self.get_category(category_name)
        logger.debug(f"current_categories: {current_categories}")

        if current_categories is None:
            current_categories = []

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
        category_id = self.get_category(category_name)[0]
        logger.debug(f"category_id: {category_id}")
        current_subcategories = map(lambda x: x[2], self.get_subcategory(category_id))

        if current_subcategories is None:
            current_subcategories = []

        if type(subcategory_name) in [str, int, float]:
            assert subcategory_name not in current_subcategories, f"Subcategories already exist: {subcategory_name}"
            self._con.execute(insert_query, {"category_id": category_id, "subcategory_name": subcategory_name})
        elif type(subcategory_name) == list:
            assert not any(map(lambda x: x in current_subcategories, subcategory_name)), f"Subcategories already exist: {', '.join(subcategory_name)}"
            args = ({"category_id": category_id, "subcategory_name": item} for item in subcategory_name)
            self._con.executemany(insert_query, args)
        else:
            raise TypeError(f"Unsupported table name type: {type(subcategory_name)}")


    def modify_category(self, old, new):
        get_category_id = "select category_id from category where category_current_name = :old and valid_to_time is NULL"
        get_subcategory_id = "select subcategory_id from subcategory where category_id = :old_category_id and valid_to_time is NULL"
        invalidate_category = "update category set valid_to_time = datetime('now') where category_id = :old_category_id"
        invalidate_subcategory = "update subcategory set valid_to_time = datetime('now') where subcategory_id = :old_subcategory_id"
                

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


