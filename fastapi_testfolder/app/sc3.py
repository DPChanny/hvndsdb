import boto3
from envs import (
    AWS_ACCESS_KEY,
    AWS_REGION,
    AWS_SECRET_KEY,
    AWS_BUCKET_NAME,
)


s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


def get_presigned_url(key):
    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": AWS_BUCKET_NAME,
            "Key": key,
            "ContentType": "image/jpeg",
        },
        ExpiresIn=3600,
    )
