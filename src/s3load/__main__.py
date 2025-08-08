"""CLI entry point for s3load."""

import argparse
from typing import List, Optional

from . import __version__
from .upload import add_upload_subparser, handle_upload


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

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_upload_subparser(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> None:  # noqa: D401
    """Run the s3load command."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "upload":
        exit_code = handle_upload(args)
        raise SystemExit(exit_code)
    # Should not reach here due to required=True subparsers
    parser.print_help()
    raise SystemExit(2)


if __name__ == "__main__":
    main()


