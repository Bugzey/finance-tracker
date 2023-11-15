"""
Tests for argparse module
"""

from argparse import ArgumentParser
import unittest

from finance_tracker.argparse import (
    Parser,
    process_data,
)


class ProcessedDataTestCase(unittest.TestCase):
    def test_processed_data(self):
        result = process_data(
            r"one=bla two='bla two' three=one\ two four=extra=equals"
        )
        self.assertEqual(
            result,
            {
                "one": "bla",
                "two": "bla two",
                "three": "one two",
                "four": "extra=equals",
            }
        )


class ArgumentParserTestCase(unittest.TestCase):
    def test_add_objects_argument(self):
        parser = ArgumentParser(prog="test")
        parser = Parser.add_objects_argument(parser)
        args = parser.parse_args(["transaction"])
        self.assertIn("object", args.__dict__)
        self.assertEqual(args.object, "transaction")

    def test_add_action(self):
        parser = ArgumentParser(prog="test")
        subparsers = parser.add_subparsers(dest="bla")
        _ = Parser().add_action(subparsers, "break", "some help")
        result = parser.parse_args(["break", "transaction"])
        self.assertIn("bla", result)
        self.assertEqual(result.bla, "break")
        self.assertIn("object", result)
        self.assertEqual(result.object, "transaction")

    def test_full(self):
        parser = Parser().get_parser()
        result = parser.parse_args([
            "create",
            "transaction",
            "id=2 amount=12 category_id=1 subcategory_id=31",
        ])
        self.assertEqual(result.action, "create")
        self.assertEqual(result.object, "transaction")
        self.assertEqual(
            result.data,
            {
                "id": "2",
                "amount": "12",
                "category_id": "1",
                "subcategory_id": "31",
            },
        )
