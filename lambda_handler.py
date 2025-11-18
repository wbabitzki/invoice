import base64
import json
from typing import Any, Dict

from invoice import render, create_file_name, test_data


def _parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract invoice data from a Lambda event.

    Accepts either a pre-parsed dictionary under the "data" key or a JSON
    string body compatible with API Gateway proxy events.
    """
    if not event:
        return test_data

    if "data" in event and isinstance(event["data"], dict):
        return event["data"]

    body = event.get("body")
    if isinstance(body, str):
        try:
            parsed_body = json.loads(body)
            if isinstance(parsed_body, dict):
                return parsed_body
        except json.JSONDecodeError:
            pass

    return test_data


def handler(event, context):
    invoice_data = _parse_event(event or {})
    pdf_bytes = render(invoice_data)
    filename = create_file_name(invoice_data)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Disposition": f"attachment; filename={filename}",
        },
        "isBase64Encoded": True,
        "body": base64.b64encode(pdf_bytes).decode("utf-8"),
    }
