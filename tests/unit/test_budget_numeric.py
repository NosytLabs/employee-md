"""Budget numeric boundaries: invalid values must never remove a cap or mutate spend."""
from concurrent.futures import ThreadPoolExecutor
import math
import sys

import pytest

from runtime import BudgetExceeded, BudgetTracker


INVALID_LIMITS = [float('nan'), float('inf'), -float('inf'), -1, '10', True, False, 10**400]
INVALID_AMOUNTS = [float('nan'), float('inf'), -float('inf'), -1, '1', None, True, False, 10**400]


@pytest.mark.parametrize('limit', INVALID_LIMITS)
def test_invalid_explicit_limit_is_not_silently_unlimited(limit):
    with pytest.raises(ValueError):
        BudgetTracker(limit)


@pytest.mark.parametrize('amount', INVALID_AMOUNTS)
def test_invalid_reservation_preserves_cap_and_spent(amount):
    tracker = BudgetTracker(10)
    tracker.try_spend(4)
    with pytest.raises(ValueError):
        tracker.try_spend(amount)
    assert tracker.spent == 4
    assert tracker.remaining() == 6
    with pytest.raises(BudgetExceeded):
        tracker.try_spend(7)
    assert tracker.spent == 4


@pytest.mark.parametrize('amount', INVALID_AMOUNTS)
def test_unlimited_tracker_still_rejects_invalid_reservations(amount):
    tracker = BudgetTracker(None)
    tracker.try_spend(2)
    with pytest.raises(ValueError):
        tracker.try_spend(amount)
    assert tracker.spent == 2
    assert tracker.remaining() is None


def test_finite_inputs_cannot_overflow_unlimited_accumulator():
    tracker = BudgetTracker(None)
    tracker.try_spend(sys.float_info.max)
    with pytest.raises(ValueError):
        tracker.try_spend(sys.float_info.max)
    assert tracker.spent == sys.float_info.max
    assert math.isfinite(tracker.spent)


def test_zero_limit_and_exact_boundary_remain_valid():
    zero = BudgetTracker(0)
    assert zero.try_spend(0)
    with pytest.raises(BudgetExceeded):
        zero.try_spend(0.25)
    tracker = BudgetTracker(1)
    for _ in range(4):
        assert tracker.try_spend(0.25)
    assert tracker.remaining() == 0
    with pytest.raises(BudgetExceeded):
        tracker.try_spend(0.25)
    tracker.reset()
    assert tracker.spent == 0
    assert tracker.remaining() == 1


def test_concurrent_valid_reservations_cannot_exceed_cap():
    tracker = BudgetTracker(3)

    def reserve(_):
        try:
            return tracker.try_spend(0.25)
        except BudgetExceeded:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        accepted = sum(pool.map(reserve, range(40)))
    assert accepted == 12
    assert tracker.spent == 3
    assert tracker.remaining() == 0
