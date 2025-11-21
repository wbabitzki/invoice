from __future__ import annotations

import base64
import json
import logging
from typing import Any, Dict

from invoice import create_file_name, render, test_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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