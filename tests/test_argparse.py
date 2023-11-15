"""
Tests for argparse module
"""

from argparse import ArgumentParser
import unittest

from finance_tracker.argparse import Parser


class ArgumentParserTestCase(unittest.TestCase):
    def test_add_objects_argument(self):
        parser = ArgumentParser(prog="test")
        parser = Parser.add_objects_argument(parser)
        args = parser.parse_args(["transaction"])
        self.assertIn("object", args.__dict__)
        self.assertEqual(args.object, "transaction")
