from stdnum.ch import esr

def to_qr_reference(raw_reference: str) -> str:
    digits = ''.join(ch for ch in raw_reference if ch.isdigit())
    check = esr.calc_check_digit(digits)
    formatted = esr.format(digits + check)
    return formatted

if __name__ == '__main__':
    print(to_qr_reference("21 00000 00000 12345"))
    print(to_qr_reference("ABC123-456.789"))
    print(to_qr_reference("91108 00207"))