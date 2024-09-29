import os
import boto3
from boto3.s3.transfer import TransferConfig
from io import BytesIO

BUCKET_ENDPOINT = os.getenv(key='BUCKET_ENDPOINT', default="http://localhost:9000")
BUCKET_ACCESS_KEY = os.getenv(key='BUCKET_ACCESS_KEY', default="s3user")
BUCKET_SECRET_KEY = os.getenv(key='BUCKET_SECRET_KEY', default="s3password")
BUCKET_NAME = os.getenv(key='BUCKET_NAME', default="thumbifybucket")


def init_bucket(connection, bucket_name=BUCKET_NAME, region=None):
    try:
        # creating bucket if not exist
        connection.head_bucket(Bucket=bucket_name)
    except connection.exceptions.ClientError as err:
        if err.response['Error']['Code'] == '404':
            if region:
                connection.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            else:
                connection.create_bucket(Bucket=bucket_name)
        else:
            raise


def conn_to_bucket(endpoint=BUCKET_ENDPOINT, user=BUCKET_ACCESS_KEY, password=BUCKET_SECRET_KEY):
    try:
        s3 = boto3.client('s3',
        aws_access_key_id=BUCKET_ACCESS_KEY,
        aws_secret_access_key=BUCKET_SECRET_KEY,
        endpoint_url=BUCKET_ENDPOINT,
        config=boto3.session.Config(signature_version='s3v4')
    )
    except Exception as err:
        raise Exception(f"Fail connecting to bucket: {err}") from err

    return s3


def save_to_s3(connection, file, filename, chunk_size_mbs=1):
    try:
        file_obj = file.file
        transfer_config = TransferConfig(multipart_chunksize=chunk_size_mbs*1024*1024)
        # blocking call, upload to bucket sending stream of chunks.
        connection.upload_fileobj(file_obj, BUCKET_NAME, filename, Config=transfer_config)
    except Exception as err:
        raise Exception(f"Fail connecting to bucket: {err}") from err


def save_to_s3_from_bytes(connection, image_data, filename, chunk_size_mbs=1):
    try:
        file_obj = BytesIO(image_data)
        transfer_config = TransferConfig(multipart_chunksize=chunk_size_mbs*1024*1024)
        connection.upload_fileobj(file_obj, BUCKET_NAME, filename, Config=transfer_config)
    except Exception as err:
        raise Exception(f"Fail connecting to bucket: {err}") from err


def read_from_s3(connection, file_key, bucket_name=BUCKET_NAME):
    try:
        obj = connection.get_object(Bucket=bucket_name, Key=file_key)
        image_data = obj['Body'].read()
        return image_data
    except Exception as err:
        raise Exception(f"Fail connecting to bucket: {err}") from err


def get_file_url(connection, file_key, bucket_name):
    url = connection.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': file_key
        },
        ExpiresIn=3600  # URL is valid for 1 hour
    )
    return url