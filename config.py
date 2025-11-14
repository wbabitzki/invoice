# -*- coding: utf-8 -*-
config = {
    "provider": {
        "name": "Ihre Firma GmbH",
        "street": "Musterstrasse",
        "house": "123",
        "zipcode": "8001",
        "city": "Zürich",
        "phone": "+41 44 123 45 67",
        "email": "info@ihre-firma.ch",
        "website": "www.ihre-firma.ch",
        "vat_number": "CHE-123.456.789 MWST",
        "account": "CH44 3199 9123 0008 8901 2",
        "account_bank": "UBS",
    }
}

# Erklärung der QR-IBAN Struktur:
#
# CH44 3000 0001 2345 6789 0
# ││   ││   └─────────────────── Kontonummer
# ││   └───────────────────────── IID (30000 = QR-IBAN!)
# │└───────────────────────────── Check-Digits
# └────────────────────────────── Ländercode
#
# Normaler IBAN hat IID: 00000-29999
# QR-IBAN hat IID:       30000-31999
#
# Mit einem QR-IBAN MUSS eine QR-Referenz verwendet werden!