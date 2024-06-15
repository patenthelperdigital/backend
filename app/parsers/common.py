import re
from typing import Optional


def format_tax_number(tax_number: str) -> str:
    if len(tax_number) < 9 or len(tax_number) > 12:
        return ""

    if len(tax_number) in (9, 11):
        return tax_number.ljust(10, "0")

    return tax_number


def reg_number_to_int(reg_number: Optional[str]) -> Optional[int]:
    if reg_number is None:
        return None
    elif reg_number.isdigit():
        reg_number = int(reg_number)
    else:
        reg_number = re.search("\d+", reg_number)
        if reg_number is not None:
            reg_number = int(reg_number[0])
        else:
            return None

    return reg_number
