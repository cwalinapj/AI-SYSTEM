from __future__ import annotations

import hashlib
import io
from typing import Any

import boto3
from botocore.config import Config

from app.config import get_settings


def _get_client() -> Any:
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload raw bytes to S3/MinIO and return the s3:// URI."""
    settings = get_settings()
    client = _get_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f"s3://{settings.s3_bucket}/{key}"


def upload_text(key: str, text: str) -> str:
    """Upload a UTF-8 string."""
    return upload_bytes(key, text.encode("utf-8"), content_type="text/plain; charset=utf-8")


def download_bytes(key: str) -> bytes:
    """Download raw bytes from S3/MinIO."""
    settings = get_settings()
    client = _get_client()
    response = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return response["Body"].read()


def download_text(key: str) -> str:
    return download_bytes(key).decode("utf-8")


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_exists(key: str) -> bool:
    settings = get_settings()
    client = _get_client()
    try:
        client.head_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except client.exceptions.ClientError:
        return False
