from app.core.utils import clamp_priority, normalize_status


def test_normalize_status():
    assert normalize_status("  em andamento ") == "Em Andamento"


def test_clamp_priority():
    assert clamp_priority(0) == 1
    assert clamp_priority(2) == 2
    assert clamp_priority(99) == 3

