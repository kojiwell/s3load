"""CLI entry point for s3load."""

import argparse
from . import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="s3load",
        description="Command-line tool for loading data to Amazon S3.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the s3load version and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:  # noqa: D401
    """Run the s3load command."""
    parser = build_parser()
    # For now, just parse the args; future subcommands will be added later.
    parser.parse_args(argv)


if __name__ == "__main__":
    main()

