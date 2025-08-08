"""Upload subcommand implementation for s3load."""

from __future__ import annotations

import argparse
import io
import logging
import os
import time
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def add_upload_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Register the 'upload' subcommand and return its parser."""
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
    upload_parser.add_argument(
        "--location",
        default="us-east-1",
        help="AWS region name (default: us-east-1).",
    )
    return upload_parser


def parse_size(size_text: str) -> int:
    """Parse human-readable size like '4k', '8m', '2g' into bytes."""
    text = size_text.strip().lower()
    if not text:
        raise ValueError("Object size must be a positive value")
    multiplier = 1
    if text.endswith("k"):
        multiplier = 1024
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1024 ** 2
        text = text[:-1]
    elif text.endswith("g"):
        multiplier = 1024 ** 3
        text = text[:-1]
    try:
        value = int(text)
    except ValueError as exc:
        raise ValueError(f"Invalid size value: {size_text}") from exc
    if value < 0:
        raise ValueError("Size must be non-negative")
    return value * multiplier


class RandomBytesIO(io.RawIOBase):
    """A file-like object that yields cryptographically random bytes up to a size."""

    def __init__(self, total_bytes: int, chunk_size: int = 1024 * 256) -> None:
        if total_bytes < 0:
            raise ValueError("total_bytes must be >= 0")
        self._remaining = total_bytes
        self._chunk_size = max(1, chunk_size)

    def readable(self) -> bool:  # type: ignore[override]
        return True

    def readinto(self, b: bytearray | memoryview) -> int:  # type: ignore[override]
        if self._remaining <= 0:
            return 0
        buffer_length = len(b)
        to_write = min(self._remaining, min(self._chunk_size, buffer_length))
        random_bytes = os.urandom(to_write)
        b[:to_write] = random_bytes
        self._remaining -= to_write
        return to_write


def get_logger() -> logging.Logger:
    log_dir = Path.home() / ".s3load"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "s3load.log"

    logger = logging.getLogger("s3load")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def handle_upload(args: argparse.Namespace) -> int:
    logger = get_logger()

    try:
        object_size_bytes = parse_size(args.object_size)
    except ValueError as exc:
        print(f"Invalid --object-size: {exc}")
        return 2

    client = boto3.client(
        "s3",
        region_name=args.location,
        endpoint_url=args.endpoint,
        aws_access_key_id=args.s3key,
        aws_secret_access_key=args.s3secret,
        verify=not args.insecure,
    )

    total_bytes = 0
    per_object_results = []
    overall_start = time.perf_counter()

    for _ in range(args.object_count):
        key = f"s3load/{uuid.uuid4().hex}"
        fileobj = io.BufferedReader(RandomBytesIO(object_size_bytes))
        start = time.perf_counter()
        try:
            client.upload_fileobj(fileobj, args.bucket, key)
        except (BotoCoreError, ClientError) as exc:
            logger.error(
                "upload_failed | endpoint=%s bucket=%s key=%s error=%s",
                args.endpoint,
                args.bucket,
                key,
                str(exc),
            )
            print(f"Upload failed for key {key}: {exc}")
            return 1
        finally:
            try:
                fileobj.close()
            except Exception:
                pass
        elapsed = time.perf_counter() - start
        total_bytes += object_size_bytes
        per_object_results.append((key, elapsed))

    overall_elapsed = time.perf_counter() - overall_start
    mb = total_bytes / (1024 * 1024)
    throughput = mb / overall_elapsed if overall_elapsed > 0 else 0.0

    logger.info(
        "upload_summary | endpoint=%s region=%s bucket=%s objects=%d size=%s total_bytes=%d duration_s=%.4f throughput_mb_s=%.4f",
        args.endpoint,
        args.location,
        args.bucket,
        args.object_count,
        args.object_size,
        total_bytes,
        overall_elapsed,
        throughput,
    )
    for key, secs in per_object_results:
        logger.info("upload_object | key=%s duration_s=%.4f", key, secs)

    print(
        f"Uploaded {args.object_count} objects of {args.object_size} to bucket '{args.bucket}' in {overall_elapsed:.3f}s. "
        f"Throughput: {throughput:.2f} MB/s"
    )
    return 0


