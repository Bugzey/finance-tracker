"""
Entry-point module
"""

from finance_tracker.argparse import Parser


if __name__ == "__main__":
    parser = Parser().get_parser()
    args = parser.parse_args()

    from finance_tracker.main import main
    main(args)
