# Fast Metadata Service

This repository contains code for metadata web service built with Fast API. 
This web service will load metadata file from a storage and return a JSON response 
to the client. Currently, the supported storages are:

- AWS S3 bucket
- Local storage

The metadata file should be named based on the token ID of the metadata 
(e.g. "1.json"). We can find the example in the `tests/test_file/metadata`
directory

## Requirements

- Python 3.9 or later

## How to use

### Read metadata from AWS S3

1. Create an AWS S3 bucket and upload the metadata to it
2. Go to the project directory and create Python virtual environment

```
python3 -m venv env
source env/bin/activate
```

3. Run `pip install -r requirements.txt` to install dependencies
4. Set the following environment variables
   - `MAX_TOKEN_ID`: The maximum token ID of metadata available
   - `METADATA_FOLDER`: The folder containing metadata files, leave empty if it's stored in the root directory
   - `S3_BUCKET_NAME`: The AWS S3 bucket name that used to store metadata
   - `STORAGE_ACCESS_KEY`: The AWS access key to access S3 bucket
   - `STORAGE_SECRET_KEY`: The AWS secret key to access S3 bucket
   - `STORAGE_TYPE`: Set `s3` if using S3 bucket
5. Run `python main.py` to start the server

### Read metadata from local storage

1. Create directory to store metadata within the project directory and save the metadata files there
2. Go to the project directory and create Python virtual environment

```
python3 -m venv env
source env/bin/activate
```

3. Run `pip install -r requirements.txt` to install dependencies
4. Set the following environment variables
    - `MAX_TOKEN_ID`: The maximum token ID of metadata available
    - `METADATA_FOLDER`: The folder containing metadata files, leave empty if it's stored in the root directory
    - `STORAGE_TYPE`: Set `local` if using local storage
5. Run `python main.py` to start the server