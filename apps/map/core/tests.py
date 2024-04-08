from apps.map.core import errors, rules


def test_tasks_is_status_code_valid() -> None:
    assert tuple(rules.tasks.is_status_code_valid(1)) == tuple()
    assert tuple(rules.tasks.is_status_code_valid(2)) == tuple()
    assert tuple(rules.tasks.is_status_code_valid(3)) == tuple()

    status_code_errors = tuple(rules.tasks.is_status_code_valid(5))

    assert len(status_code_errors) == 1
    assert isinstance(status_code_errors[0], errors.UnknownTaskStatus)
