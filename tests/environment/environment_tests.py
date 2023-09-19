import pytest
from fabelcommon.environment.environment import (
    get_env_bool,
    get_env_int,
    get_env_float,
    get_env_str,
    get_env_str_optional
)


@pytest.mark.parametrize('key, key_value, default_value, expected_value', [
    ('STRING_ENV', 'Hello, World!', '', 'Hello, World!'),
    ('STRING_ENV', None, 'Hello, World!', 'Hello, World!')
])
def test_get_env_str(
        key,
        key_value,
        default_value,
        expected_value,
        monkeypatch
):
    if key_value is not None:
        monkeypatch.setenv(key, key_value)
    result = get_env_str(key, default_value)
    assert result == expected_value


@pytest.mark.parametrize('key, key_value, default_value, expected_value', [
    ('STRING_ENV', 'Hello, World!', '', 'Hello, World!'),
    ('STRING_ENV', 'Hello, World!', None, 'Hello, World!'),
    ('STRING_ENV', None, 'Hello, World!', 'Hello, World!'),
    ('STRING_ENV', None, None, None)
])
def test_get_env_str_optional(
        key,
        key_value,
        default_value,
        expected_value,
        monkeypatch
):
    if key_value is not None:
        monkeypatch.setenv(key, key_value)
    result = get_env_str_optional(key, default_value)
    assert result == expected_value


@pytest.mark.parametrize('key, key_value, default_value, expected_result', [
    ('DEBUG', 'true', False, True),
    ('DEBUG', 'True', False, True),
    ('DEBUG', '1', False, True),
    ('DEBUG', 'ON', False, True),
    ('DEBUG', 'false', False, False),
    ('DEBUG', 'False', False, False),
    ('DEBUG', 'False', True, False),
    ('DEBUG_X', None, True, True),
    ('DEBUG_X', None, False, False)
])
def test_get_existing_env_bool(
        key,
        key_value,
        default_value,
        expected_result,
        monkeypatch
):
    if key_value is not None:
        monkeypatch.setenv(key, key_value)
    actual_result = get_env_bool(key, default_value)
    assert actual_result == expected_result


@pytest.mark.parametrize('key, key_value, default_value, expected_result', [
    ('INTEGER_ENV', '42', 0, 42),
    ('NEGATIVE_INTEGER_ENV', '-10', -1, -10),
    ('ZERO_ENV', '0', 100, 0),
    ('INVALID_VALUE_ENV', None, 123, 123)
])
def test_get_existing_env_int(key, key_value, default_value, expected_result, monkeypatch):
    if key_value is not None:
        monkeypatch.setenv(key, key_value)
    actual_result = get_env_int(key, default_value)
    assert actual_result == expected_result


@pytest.mark.parametrize('key, key_value, default_value, expected_result', [
    ('FLOAT_ENV', '42.1', 0, 42.1),
    ('NEGATIVE_FLOAT_ENV', '-10.9', 0, -10.9),
    ('ZERO_ENV', '0', 100, 0),
    ('INVALID_VALUE_ENV', None, 123.00, 123.00)
])
def test_get_existing_env_float(key, key_value, default_value, expected_result, monkeypatch):
    if key_value is not None:
        monkeypatch.setenv(key, key_value)
    actual_result = get_env_float(key, default_value)
    assert actual_result == expected_result
