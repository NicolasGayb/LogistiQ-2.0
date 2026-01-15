import re

def normalize_cnpj(value: str) -> str:
    digits = re.sub(r"\D", "", value)

    if len(digits) != 14:
        raise ValueError("CNPJ must contain exactly 14 numeric digits")

    return digits
