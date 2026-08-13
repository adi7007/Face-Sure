"""
Unit tests for security hashing and JWT token management.
"""

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    """Test password hashing and verification with bcrypt."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_jwt_token_generation_and_decoding():
    """Test JWT access token creation and claim extraction."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    role = "ADMIN"
    extra_claims = {"email": "admin@project.edu", "name": "Admin User"}

    token = create_access_token(subject=user_id, role=role, extra_claims=extra_claims)
    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["email"] == "admin@project.edu"
    assert payload["name"] == "Admin User"
    assert "exp" in payload
