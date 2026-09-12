"""Constructor integration must preserve the numeric guard without schema validation."""
import pytest
from runtime.employee import Employee


@pytest.mark.parametrize('limit', [float('nan'), float('inf'), -1, True, 'unlimited'])
def test_employee_constructor_rejects_invalid_budget_without_schema_validation(limit):
    with pytest.raises(ValueError):
        Employee({'role': {'title': 'Test'}, 'lifecycle': {'status': 'active'},
                  'economy': {'budget_limit': limit}})
