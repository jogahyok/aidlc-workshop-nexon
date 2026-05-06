import pytest


@pytest.fixture
def jwt_secret():
    return "test_secret_key_for_unit_tests_at_least_32_chars"
