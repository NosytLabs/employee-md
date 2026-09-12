"""Invalid numeric values must not disable an agent's in-process budget."""
from concurrent.futures import ThreadPoolExecutor
import math
import sys

import pytest
from runtime.employee import BudgetExceeded, BudgetTracker, Employee

INVALID = [float('nan'), float('inf'), float('-inf'), -1, True, False, '10', [], {}]


@pytest.mark.parametrize('limit', INVALID)
def test_invalid_explicit_limit_is_not_silently_unlimited(limit):
    with pytest.raises(ValueError):
        BudgetTracker(limit)


@pytest.mark.parametrize('limit', [None, 2.0])
@pytest.mark.parametrize('amount', INVALID + [None])
def test_invalid_spend_does_not_corrupt_accounting(limit, amount):
    tracker = BudgetTracker(limit)
    tracker.try_spend(0.5)
    with pytest.raises(ValueError):
        tracker.try_spend(amount)
    assert tracker.spent == 0.5
    assert math.isfinite(tracker.spent)
    assert tracker.remaining() == (None if limit is None else 1.5)


@pytest.mark.parametrize('kind', ['limit', 'amount'])
def test_unrepresentable_integer_is_a_validation_error(kind):
    tracker = BudgetTracker(None)
    with pytest.raises(ValueError):
        if kind == 'limit':
            BudgetTracker(10 ** 400)
        else:
            tracker.try_spend(10 ** 400)
    assert tracker.spent == 0


def test_non_finite_total_does_not_corrupt_unlimited_tracker():
    tracker = BudgetTracker(None)
    tracker.try_spend(sys.float_info.max)
    with pytest.raises(ValueError):
        tracker.try_spend(sys.float_info.max)
    assert tracker.spent == sys.float_info.max
    assert tracker.remaining() is None


def test_invalid_amount_cannot_poison_subsequent_limit_check():
    tracker = BudgetTracker(1.0)
    with pytest.raises(ValueError):
        tracker.try_spend(float('nan'))
    with pytest.raises(BudgetExceeded):
        tracker.try_spend(2.0)
    assert tracker.spent == 0.0


def test_none_remains_an_explicit_uncapped_tracker():
    tracker = BudgetTracker(None)
    assert tracker.try_spend(123.0)
    assert tracker.spent == 123.0
    assert tracker.remaining() is None
    tracker.reset()
    assert tracker.spent == 0.0


def test_zero_budget_is_a_real_cap():
    tracker = BudgetTracker(0)
    assert tracker.try_spend(0)
    with pytest.raises(BudgetExceeded):
        tracker.try_spend(0.01)
    assert tracker.limit == tracker.spent == tracker.remaining() == 0


def test_exact_limit_and_rejected_spend_are_atomic():
    tracker = BudgetTracker(1.0)
    tracker.try_spend(0.25)
    tracker.try_spend(0.75)
    with pytest.raises(BudgetExceeded) as error:
        tracker.try_spend(0.25)
    assert (error.value.requested, error.value.spent, error.value.limit) == (0.25, 1.0, 1.0)
    assert tracker.spent == 1.0


def test_concurrent_reservations_do_not_exceed_cap():
    tracker = BudgetTracker(5.0)

    def reserve(_):
        try:
            return tracker.try_spend(0.25)
        except BudgetExceeded:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(reserve, range(100)))
    assert sum(results) == 20
    assert tracker.spent == 5.0
    assert tracker.remaining() == 0.0


@pytest.mark.parametrize('limit', [float('nan'), float('inf'), -1, True, 'unlimited'])
def test_employee_constructor_rejects_invalid_budget_even_without_schema_validation(limit):
    with pytest.raises(ValueError):
        Employee({'role': {'title': 'Test'}, 'lifecycle': {'status': 'active'}, 'economy': {'budget_limit': limit}})
