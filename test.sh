#!/usr/bin/env sh

MAX_TOKEN_ID=5 \
METADATA_FOLDER=tests/test_file/metadata \
STORAGE_TYPE=local \
S3_BUCKET_NAME=tests \
coverage run -m unittest
coverage report
