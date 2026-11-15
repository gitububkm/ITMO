import jwt
from app.core.config import settings
from app.core.security import create_access_token, generate_short_code, hash_password, verify_password
from app.services.click_tasks import deactivate_expired_links_sync, record_click_sync


def test_password_hash_and_verify() -> None:
    hashed = hash_password("secret123")
    assert verify_password(hashed, "secret123")
    assert not verify_password(hashed, "wrong")


def test_generate_short_code_length() -> None:
    length = 10
    code = generate_short_code(length)
    assert len(code) == length
    assert code.isalnum()


def test_create_access_token_contains_sub() -> None:
    token = create_access_token("user-id-1")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-id-1"


def test_record_click_and_expire_helpers_importable() -> None:
    assert callable(record_click_sync)
    assert callable(deactivate_expired_links_sync)
