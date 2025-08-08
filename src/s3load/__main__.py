"""CLI entry point for s3load."""

import argparse
from typing import List, Optional

from . import __version__
from .upload import handle_upload


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

    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload random objects to an S3 bucket and measure performance.",
    )
    upload_parser.add_argument(
        "-e",
        "--endpoint",
        required=True,
        help="S3 endpoint URL (e.g., https://s3.amazonaws.com or custom).",
    )
    upload_parser.add_argument(
        "--s3key",
        required=True,
        help="S3 access key (AWS access key ID).",
    )
    upload_parser.add_argument(
        "--s3secret",
        required=True,
        help="S3 secret key (AWS secret access key).",
    )
    upload_parser.add_argument(
        "-b",
        "--bucket",
        required=True,
        help="Target S3 bucket name.",
    )
    upload_parser.add_argument(
        "-n",
        "--object-count",
        "--object--count",
        dest="object_count",
        type=int,
        default=100,
        help="Number of objects to upload (default: 100).",
    )
    upload_parser.add_argument(
        "-s",
        "--object-size",
        default="4k",
        help="Object size, accepts suffix k/m/g (e.g., 4k, 8m, 2g). Default: 4k.",
    )
    upload_parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS/SSL certificate verification (NOT recommended).",
    )

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


