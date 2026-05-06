"""Property-based tests for JWT and password hashing (PBT-02: Round-trip)."""
from unittest.mock import patch

from hypothesis import given, settings as hyp_settings
from hypothesis import strategies as st

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@given(password=st.text(min_size=1, max_size=72, alphabet=st.characters(blacklist_categories=("Cs",))))
@hyp_settings(max_examples=10)
def test_password_hash_roundtrip(password: str):
    """PBT-02: verify(password, hash(password)) == True for all valid passwords."""
    # bcrypt has a 72-byte limit; filter out strings that exceed it when encoded
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        return  # skip inputs that exceed bcrypt's limit
    hashed = hash_password(password)
    assert verify_password(password, hashed)


@given(password=st.text(min_size=1, max_size=72, alphabet=st.characters(blacklist_categories=("Cs",))))
@hyp_settings(max_examples=10)
def test_password_hash_different_input_fails(password: str):
    """Verify that wrong password does not match."""
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        return  # skip inputs that exceed bcrypt's limit
    hashed = hash_password(password)
    wrong = password + "x"
    if len(wrong.encode("utf-8")) > 72:
        return
    assert not verify_password(wrong, hashed)


@given(
    subject=st.integers(min_value=1, max_value=10000),
    store_id=st.integers(min_value=1, max_value=10000),
    token_type=st.sampled_from(["admin", "table"]),
    table_number=st.one_of(st.none(), st.integers(min_value=1, max_value=100)),
)
@hyp_settings(max_examples=50)
def test_jwt_roundtrip(subject: int, store_id: int, token_type: str, table_number):
    """PBT-02: decode(encode(payload)) preserves sub, store_id, type."""
    with patch("app.core.security.settings") as mock_settings:
        mock_settings.jwt_secret_key = "test_secret_key_for_unit_tests_at_least_32_chars"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_expire_hours = 16

        token = create_access_token(subject, store_id, token_type, table_number)
        payload = decode_access_token(token)

        assert int(payload["sub"]) == subject
        assert payload["store_id"] == store_id
        assert payload["type"] == token_type
        if table_number is not None:
            assert payload["table_number"] == table_number
