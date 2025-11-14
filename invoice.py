# -*- coding: utf-8 -*-
import json
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path
from typing import Optional, Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from referenznummer import to_qr_reference
from config import config
from swiss_bill_generator import create_qr_svg

test_data = {
    "customer": {
        "name": "Peter Mustermann",
        "street": "Strasse",
        "house": "100",
        "zipcode": "8888",
        "city": "Luzern",
    },
    "invoice": {"number": "2025-001", "date": "12.08.2025", "name": "Juni 2025"},
    "items": [
        {"desc": "Provision gemäss dem Vertrag vom 11.11.2024", "qty": 150, "unit_price": 25.00,
         "price_unit": "Stunden"},
        {"desc": "Käseplatte", "qty": 50, "unit_price": 12.00, "price_unit": "Stunden"},
    ],
    "currency": "CHF",
    "provider": config["provider"],
}
BASE_DIR = Path(__file__).parent.resolve()
TEST_OUTPUT = BASE_DIR / "output/invoice.pdf"

def swiss_number(value):
    try:
        formatted = f"{float(value):,.2f}"
        return formatted.replace(",", "'")
    except:
        return value

def calculate_totals(
        data: Dict[str, Any],
        vat_rate: float = 8.10
) -> Dict[str, Any]:

    # Use Decimal for precise financial calculations
    net = Decimal(0)
    for item in data["items"]:
        qty = Decimal(str(item["qty"]))
        unit_price = Decimal(str(item["unit_price"]))
        net += qty * unit_price

    vat_rate_decimal = Decimal(str(vat_rate))
    vat = (net * vat_rate_decimal / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    gross = net + vat

    # Convert back to float for template rendering
    data["totals"] = {
        "net": float(net),
        "vat_rate": vat_rate,
        "vat": float(vat),
        "gross": float(gross),
    }
    return data

@lru_cache(maxsize=1)
def get_env(base_dir: Optional[Path] = None) -> Environment:
    root = (base_dir or BASE_DIR).resolve()
    env = Environment(
        loader=FileSystemLoader(str(root)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["swiss"] = swiss_number
    return env

def render(data_: Dict[str, Any]):
    env = get_env(BASE_DIR)
    template = env.get_template("./templates/invoice.html")

    data_ = calculate_totals(data_)
    data_["reference"] = to_qr_reference(data_["invoice"]["number"])
    qr = create_qr_svg(data_)
    html_str = template.render(**data_, qr_svg=qr)
    return HTML(string=html_str, base_url=BASE_DIR.as_posix()).write_pdf()

def create_file_name(data_: Dict[str, Any]) -> str:
    invoice_date = datetime.strptime(data_['invoice']['date'], "%d.%m.%Y").date()
    invoice_number = data_['invoice']['number'].replace(" ", "-")
    return f"{invoice_date}_{invoice_number}.pdf"

if __name__ == "__main__":
    if len(sys.argv) == 1:
        TEST_OUTPUT.write_bytes(render(test_data))
        print(f"PDF erstellt: {TEST_OUTPUT}")
    else:
        with open(sys.argv[1], 'r') as file:
            data = json.load(file)
        file_name = create_file_name(data)
        print(file_name)
        (BASE_DIR / "output" / file_name).write_bytes(render(data))
