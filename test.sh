#!/usr/bin/env sh

MAX_TOKEN_ID=4 \
METADATA_FOLDER=tests/test_file/metadata \
STORAGE_TYPE=local \
S3_BUCKET_NAME=test \
coverage run -m unittest