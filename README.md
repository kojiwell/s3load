# s3load

Command-line tool for loading data to Amazon S3 (or S3-compatible) services.

## Installation

Recommended with a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## CLI

Show top-level help:

```bash
s3load --help
```

Show version:

```bash
s3load --version
```

### Upload subcommand

Upload randomly generated objects and measure performance. Logs are written to `~/.s3load/s3load.log`.

```bash
s3load upload --help
```

Options:

- `-e, --endpoint` S3 endpoint URL (e.g., `https://s3.amazonaws.com`)
- `--s3key` AWS access key ID
- `--s3secret` AWS secret access key
- `-b, --bucket` Target S3 bucket name
- `-n, --object-count` Number of objects to upload (default: 100)
- `-s, --object-size` Object size, accepts suffix k/m/g (e.g., `4k`, `8m`, `2g`), default `4k`
- `--insecure` Disable TLS/SSL certificate verification (NOT recommended)

Example:

```bash
s3load upload \
  -e https://s3.amazonaws.com \
  --s3key "$AWS_ACCESS_KEY_ID" \
  --s3secret "$AWS_SECRET_ACCESS_KEY" \
  -b my-bucket \
  -n 1000 \
  -s 8m
```

For S3-compatible services (e.g., MinIO), set the custom `--endpoint`. Use `--insecure` only for testing self-signed TLS.

