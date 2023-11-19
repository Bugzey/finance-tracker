"""
Entry-point module
"""

from finance_tracker.argparse import Parser


def main():
    parser = Parser().get_parser()
    args = parser.parse_args()

    from finance_tracker.main import main as inner_main
    inner_main(args)


if __name__ == "__main__":
    main()
