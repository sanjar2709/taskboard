import pytest

from apps.common.ordering import MIN_GAP, STEP, neighbours, position_between, renumbered


@pytest.mark.parametrize(('before', 'after', 'expected'), (
    (None, None, STEP),
    (None, 1024.0, 512.0),
    (1024.0, None, 2048.0),
    (1024.0, 2048.0, 1536.0),
))
def test_position_between(before, after, expected):
    assert position_between(before, after) == expected


def test_too_small_gap_asks_for_renumbering():
    assert position_between(1.0, 1.0 + MIN_GAP / 2) is None
    assert position_between(None, MIN_GAP / 2) is None


@pytest.mark.parametrize(('index', 'expected'), (
    (0, (None, 10.0)),
    (1, (10.0, 20.0)),
    (3, (30.0, None)),
    (99, (30.0, None)),  # out of range means "at the end"
))
def test_neighbours(index, expected):
    assert neighbours([10.0, 20.0, 30.0], index) == expected


def test_renumbered():
    assert renumbered(3) == [STEP, STEP * 2, STEP * 3]


def test_many_inserts_into_same_gap_eventually_need_renumbering():
    before, after = 1024.0, 2048.0
    for _ in range(100):
        middle = position_between(before, after)
        if middle is None:
            break
        after = middle
    else:
        pytest.fail('Gap never became too small')
