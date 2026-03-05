def normalize_status(text: str) -> str:
    return text.strip().title()


def clamp_priority(value: int) -> int:
    return max(1, min(3, value))

