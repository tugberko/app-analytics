import hashlib


def digest(input_string: str) -> str:
    return hashlib.sha256(input_string.encode()).hexdigest()