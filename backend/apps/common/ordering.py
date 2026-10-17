"""Ordering of columns and tasks with fractional positions.

Moving an item only changes its own position: it gets the middle value between its new neighbours.
After many moves into the same spot the gap gets tiny, then the whole list is renumbered once.
"""

STEP = 1024.0
MIN_GAP = 1e-6


def position_between(before: float | None, after: float | None) -> float | None:
    """Position for an item placed between two neighbours. None means the list needs renumbering."""
    if before is None and after is None:
        return STEP
    if before is None:
        return after / 2 if after > MIN_GAP else None
    if after is None:
        return before + STEP
    if after - before < MIN_GAP:
        return None
    return (before + after) / 2


def neighbours(positions: list[float], index: int) -> tuple[float | None, float | None]:
    """Neighbours for inserting at `index` into an already sorted list (the moved item not included)."""
    index = max(0, min(index, len(positions)))
    before = positions[index - 1] if index > 0 else None
    after = positions[index] if index < len(positions) else None
    return before, after


def renumbered(count: int) -> list[float]:
    return [STEP * (i + 1) for i in range(count)]
