import re
from decimal import Decimal
from typing import cast


def record(value: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} requires exactly these fields: {', '.join(sorted(fields))}")
    return cast(dict[str, object], value)


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(character) < 32 for character in value):
        raise ValueError(f"{label} must be nonempty text without control characters")
    return value


def sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return cast(list[object], value)


def positive_integer(value: object, label: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def decimal_string(value: object, label: str, money: bool = False) -> Decimal:
    pattern = r"[0-9]+(?:\.[0-9]{1,2})?" if money else r"[0-9]+(?:\.[0-9]+)?"
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValueError(f"{label} must be a nonnegative decimal string" + (" with at most two decimal places" if money else ""))
    return Decimal(value)
