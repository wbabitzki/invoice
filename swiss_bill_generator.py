#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Dict, Any

import segno

QR_SIZE_MM = 46.0
QUIET_ZONE_MODULES = 4
SWISS_CROSS_SIZE_MM = 7.0

@dataclass
class SwissQRData:
    """Swiss QR Bill example data based on SIX Implementation Guidelines v2.3 (20.11.2023)"""
    # Header
    QRType: str = "SPC"
    Version: str = "0200"
    Coding_Type: str = "1"
    Konto: str = "CH1030000001600001411"

    # Creditor (Zahlungsempfänger, ZE)
    ZE_Adress_Typ: str = "S"
    ZE_Name: str = "Max Muster & Söhne"
    ZE_Strasse: str = "Musterstrasse"
    ZE_Hausnummer: str = "123"
    ZE_Postleitzahl: str = "8000"
    ZE_Ort: str = "Seldwyla"
    ZE_Land: str = "CH"

    # Ultimate Creditor (EZE)
    EZE_Adress_Typ: str = ""
    EZE_Name: str = ""
    EZE_Strasse: str = ""
    EZE_Hausnummer: str = ""
    EZE_Postleitzahl: str = ""
    EZE_Ort: str = ""
    EZE_Land: str = ""

    # Amount and currency
    Betrag: str = "50.00"
    Waehrung: str = "CHF"

    # Debtor (Zahlungspflichtiger, EZP)
    EZP_Adress_Typ: str = "S"
    EZP_Name: str = "Simon Muster"
    EZP_Strasse: str = "Musterstrasse"
    EZP_Hausnummer: str = "1"
    EZP_Postleitzahl: str = "8000"
    EZP_Ort: str = "Seldwyla"
    EZP_Land: str = "CH"

    # Reference and message
    Referenztyp: str = "QRR"
    Referenz: str = "000008207791225857421286694"
    Unstrukturierte_Mitteilung: str = "Bezahlung der Reise"

    # Trailer and optional parameters
    Trailer: str = "EPD"
    Rechnungsinformationen: str = ""
    AV1_Parameter: str = ""
    AV2_Parameter: str = ""

    def to_spc_payload(self) -> str:
        lines = [
            self.QRType,  # 1
            self.Version,  # 2
            self.Coding_Type,  # 3
            self.Konto,  # 4

            # Creditor (ZE) – 5..11
            self.ZE_Adress_Typ,
            self.ZE_Name,
            self.ZE_Strasse,
            self.ZE_Hausnummer,
            self.ZE_Postleitzahl,
            self.ZE_Ort,
            self.ZE_Land,

            # Ultimate Creditor (EZE) – 12..18
            self.EZE_Adress_Typ,
            self.EZE_Name,
            self.EZE_Strasse,
            self.EZE_Hausnummer,
            self.EZE_Postleitzahl,
            self.EZE_Ort,
            self.EZE_Land,

            # Amount & currency – 19..20
            self.Betrag,
            self.Waehrung,

            # Debtor (EZP) – 21..27
            self.EZP_Adress_Typ,
            self.EZP_Name,
            self.EZP_Strasse,
            self.EZP_Hausnummer,
            self.EZP_Postleitzahl,
            self.EZP_Ort,
            self.EZP_Land,

            # Reference & info – 28..34
            self.Referenztyp,  # 28
            self.Referenz,  # 29
            self.Unstrukturierte_Mitteilung,  # 30
            self.Trailer,  # 31
        ]
        return "\n".join(lines)

    @classmethod
    def from_data(cls, data):
        creditor = data.get("provider")
        debitor = data.get("customer")
        return cls(
            Konto=creditor.get("account").replace(" ", ""),
            ZE_Name=creditor.get("name"),
            ZE_Strasse=creditor.get("street"),
            ZE_Hausnummer=creditor.get("house"),
            ZE_Postleitzahl=creditor.get("zipcode"),
            ZE_Ort=creditor.get("city"),

            EZP_Name=debitor.get("name"),
            EZP_Strasse=debitor.get("street"),
            EZP_Hausnummer=debitor.get("house"),
            EZP_Postleitzahl=debitor.get("zipcode"),
            EZP_Ort=debitor.get("city"),

            Betrag="{:.2f}".format(data.get("totals").get("gross")),
            Waehrung=data.get("currency"),
            Referenz=data.get("reference").replace(" ", ""),
        )


def create_qr_svg(data: Dict[str, Any], ) -> str:
    qr_data = SwissQRData.from_data(data)
    payload_ = qr_data.to_spc_payload()
    qr = segno.make(payload_, micro=False, error='m', encoding='utf-8')
    sz = qr.symbol_size(border=0)
    symbol_modules = int(getattr(sz, "width", sz[0]))

    scale_mm_per_module = QR_SIZE_MM / float(symbol_modules)

    svg = qr.svg_inline(
        unit="mm",
        scale=scale_mm_per_module,
        border=0,
    )

    if 'xmlns=' not in svg:
        svg = svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)

    return svg

def create_swiss_qr(_filename, _payload):
    svg = create_qr_svg(_payload)
    with open(_filename, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    payload = SwissQRData().to_spc_payload()
    create_swiss_qr("qr_composed.svg", payload)
    print("✅ wrote qr_composed.svg")