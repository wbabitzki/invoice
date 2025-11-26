from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

from invoice import create_file_name, render, test_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

s3_client = boto3.client("s3")

def _extract_payload(event):
    if not isinstance(event, dict) or not event:
        return dict(test_data)

    if "body" in event:
        body = event["body"]
        if body is None or (isinstance(body, str) and not body.strip()):
            return dict(test_data)

        if isinstance(body, str):
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return dict(test_data)
        elif isinstance(body, dict):
            data = body
        else:
            return dict(test_data)

        if not isinstance(data, dict) or not data.get("items"):
            return dict(test_data)
        return data

    if "invoice" in event and "items" in event:
        return event

    return dict(test_data)


def lambda_handler(event: Dict[str, Any] | None, _context: Any) -> Dict[str, Any]:
    logger.info("lambda_handler start")
    payload = _extract_payload(event)
    logger.info("payload extracted")

    logger.info("calling render()")
    pdf_bytes = render(payload)
    logger.info("render() finished, %d bytes", len(pdf_bytes))

    file_name = create_file_name(payload)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Disposition": f'attachment; filename="{file_name}"',
        },
        "isBase64Encoded": True,
        "body": base64.b64encode(pdf_bytes).decode("utf-8"),
    }

def lambda_handler_s3(event: Dict[str, Any] | None, _context: Any) -> Dict[str, Any]:

    logger.info("lambda_handler_s3 start")
    payload = _extract_payload(event)
    logger.info("payload extracted")

    file_name = create_file_name(payload)

    logger.info("calling render()")
    pdf_bytes = render(payload)
    logger.info("render() finished, %d bytes", len(pdf_bytes))

    bucket_name = os.getenv("PDF_BUCKET_NAME")
    if not bucket_name:
        logger.error("PDF_BUCKET_NAME environment variable is not set")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Server misconfiguration: bucket not set"}),
        }

    key_prefix = os.getenv("PDF_KEY_PREFIX", "")
    if key_prefix and not key_prefix.endswith("/"):
        key_prefix = f"{key_prefix}/"
    object_key = f"{key_prefix}{file_name}"

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=pdf_bytes,
            ContentType="application/pdf",
            ServerSideEncryption="aws:kms",
        )
        logger.info("PDF uploaded to s3://%s/%s", bucket_name, object_key)
    except ClientError:
        logger.exception("Failed to upload PDF to S3")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Unable to store PDF"}),
        }

    expires_in = os.getenv("PRESIGNED_URL_EXPIRATION", "3600")
    try:
        expires_int = int(expires_in)
    except ValueError:
        logger.warning("Invalid PRESIGNED_URL_EXPIRATION '%s', using default", expires_in)
        expires_int = 3600

    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expires_int,
        )
        logger.info("Pre-signed URL generated")
    except ClientError:
        logger.exception("Failed to generate pre-signed URL")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Unable to generate access URL"}),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"fileName": file_name, "url": presigned_url}),
    }