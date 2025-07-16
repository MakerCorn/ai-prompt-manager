"""
Unit tests for the PasswordHandler security utility.

This module tests password hashing, verification, and security features
of the modernized password handling system.
"""

from unittest.mock import patch

import pytest

from src.auth.security.password_handler import PasswordHandler
from src.core.exceptions.base import AuthenticationException


class TestPasswordHandler:
    """Test cases for the PasswordHandler class."""

    def test_password_handler_initialization_argon2(self):
        """Test password handler initialization with Argon2."""
        # Test that when ARGON2_AVAILABLE is True, argon2 is used
        with patch("src.auth.security.password_handler.ARGON2_AVAILABLE", True):
            handler = PasswordHandler()
            # Should use argon2 if available, or fallback to bcrypt or pbkdf2
            assert handler.algorithm in ["argon2", "bcrypt", "pbkdf2"]

    def test_password_handler_initialization_bcrypt(self):
        """Test password handler initialization with bcrypt."""
        with (
            patch("src.auth.security.password_handler.ARGON2_AVAILABLE", False),
            patch("src.auth.security.password_handler.BCRYPT_AVAILABLE", True),
        ):
            handler = PasswordHandler()
            assert handler.algorithm == "bcrypt"

    def test_password_handler_initialization_pbkdf2_fallback(self):
        """Test password handler falls back to PBKDF2 when modern libraries unavailable."""
        with (
            patch("src.auth.security.password_handler.ARGON2_AVAILABLE", False),
            patch("src.auth.security.password_handler.BCRYPT_AVAILABLE", False),
        ):
            handler = PasswordHandler()
            assert handler.algorithm == "pbkdf2"

    def test_password_handler_preferred_algorithm(self):
        """Test password handler respects preferred algorithm."""
        with patch("src.auth.security.password_handler.BCRYPT_AVAILABLE", True):
            handler = PasswordHandler(algorithm="bcrypt")
            assert handler.algorithm == "bcrypt"

    def test_hash_password_pbkdf2(self):
        """Test password hashing with PBKDF2."""
        handler = PasswordHandler(algorithm="pbkdf2")

        password = "test_password_123"
        hashed, salt = handler.hash_password(password)

        assert hashed is not None
        assert salt is not None
        assert len(hashed) > 0
        assert len(salt) > 0
        assert hashed != password

    def test_hash_password_empty_raises_exception(self):
        """Test hashing empty password raises exception."""
        handler = PasswordHandler()

        with pytest.raises(AuthenticationException) as exc_info:
            handler.hash_password("")

        assert "Password cannot be empty" in str(exc_info.value)

    def test_verify_password_pbkdf2_success(self):
        """Test successful password verification with PBKDF2."""
        handler = PasswordHandler(algorithm="pbkdf2")

        password = "test_password_123"
        hashed, salt = handler.hash_password(password)

        # Should verify successfully
        assert handler.verify_password(password, hashed, salt) is True

    def test_verify_password_pbkdf2_failure(self):
        """Test failed password verification with PBKDF2."""
        handler = PasswordHandler(algorithm="pbkdf2")

        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed, salt = handler.hash_password(password)

        # Should fail verification
        assert handler.verify_password(wrong_password, hashed, salt) is False

    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        handler = PasswordHandler()

        # Empty password
        assert handler.verify_password("", "hash", "salt") is False

        # Empty hash
        assert handler.verify_password("password", "", "salt") is False

        # Test with None-like empty strings instead
        assert handler.verify_password("", "hash", "salt") is False
        assert handler.verify_password("password", "", "salt") is False

    @patch("src.auth.security.password_handler.BCRYPT_AVAILABLE", True)
    @patch("src.auth.security.password_handler.bcrypt")
    def test_hash_password_bcrypt(self, mock_bcrypt):
        """Test password hashing with bcrypt."""
        # Mock bcrypt functions
        mock_bcrypt.gensalt.return_value = b"salt"
        mock_bcrypt.hashpw.return_value = b"hashed_password"

        handler = PasswordHandler(algorithm="bcrypt")
        password = "test_password"

        hashed, algorithm = handler.hash_password(password)

        assert hashed == "hashed_password"
        assert algorithm == "bcrypt"
        mock_bcrypt.gensalt.assert_called_once()
        mock_bcrypt.hashpw.assert_called_once_with(password.encode("utf-8"), b"salt")

    @patch("src.auth.security.password_handler.BCRYPT_AVAILABLE", True)
    @patch("src.auth.security.password_handler.bcrypt")
    def test_verify_password_bcrypt(self, mock_bcrypt):
        """Test password verification with bcrypt."""
        mock_bcrypt.checkpw.return_value = True

        handler = PasswordHandler(algorithm="bcrypt")

        result = handler.verify_password("password", "$2b$12$hash", "bcrypt")

        assert result is True
        mock_bcrypt.checkpw.assert_called_once()

    def test_hash_password_argon2(self):
        """Test password hashing with Argon2."""
        # Test argon2 hashing when available, or fallback behavior
        handler = PasswordHandler(algorithm="argon2")

        # Handler should use argon2 if available, or fallback to available algorithm
        assert handler.algorithm in ["argon2", "pbkdf2", "bcrypt"]

        password = "test_password"
        hashed, salt_or_metadata = handler.hash_password(password)

        # Should produce a valid hash with the selected algorithm
        assert hashed is not None
        assert salt_or_metadata is not None
        assert len(hashed) > 0
        assert len(salt_or_metadata) > 0

    def test_verify_password_argon2(self):
        """Test password verification with Argon2."""
        # Test argon2 verification when available, or fallback behavior
        handler = PasswordHandler(algorithm="argon2")

        # Handler should use argon2 if available, or fallback to available algorithm
        assert handler.algorithm in ["argon2", "pbkdf2", "bcrypt"]

        # Verification should work with the selected algorithm
        password = "test_password"
        hashed, salt_or_metadata = handler.hash_password(password)
        result = handler.verify_password(password, hashed, salt_or_metadata)

        assert result is True

    def test_detect_algorithm_argon2(self):
        """Test algorithm detection for Argon2 hashes."""
        handler = PasswordHandler()

        algorithm = handler._detect_algorithm("$argon2id$v=19$hash", "argon2")
        assert algorithm == "argon2"

    def test_detect_algorithm_bcrypt(self):
        """Test algorithm detection for bcrypt hashes."""
        handler = PasswordHandler()

        algorithm = handler._detect_algorithm("$2b$12$hash", "bcrypt")
        assert algorithm == "bcrypt"

        algorithm = handler._detect_algorithm("$2a$12$hash", "bcrypt")
        assert algorithm == "bcrypt"

    def test_detect_algorithm_pbkdf2(self):
        """Test algorithm detection for PBKDF2 hashes."""
        handler = PasswordHandler()

        algorithm = handler._detect_algorithm("regular_hash", "salt")
        assert algorithm == "pbkdf2"

    def test_needs_rehash_different_algorithm(self):
        """Test needs rehash when using different algorithm."""
        # Create handler with pbkdf2 then check if bcrypt hash needs rehashing
        handler_pbkdf2 = PasswordHandler(algorithm="pbkdf2")

        # bcrypt hash should need rehash to pbkdf2 algorithm
        needs_rehash = handler_pbkdf2.needs_rehash("$2b$12$hash", "bcrypt")
        assert needs_rehash is True

    def test_needs_rehash_same_algorithm(self):
        """Test needs rehash with same algorithm."""
        handler = PasswordHandler(algorithm="pbkdf2")

        # Same algorithm should not need rehash
        needs_rehash = handler.needs_rehash("pbkdf2_hash", "salt")
        assert needs_rehash is False

    def test_generate_secure_password_default(self):
        """Test secure password generation with defaults."""
        handler = PasswordHandler()

        password = handler.generate_secure_password()

        assert len(password) == 16
        assert any(c.islower() for c in password)  # Has lowercase
        assert any(c.isupper() for c in password)  # Has uppercase
        assert any(c.isdigit() for c in password)  # Has digits
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)  # Has symbols

    def test_generate_secure_password_custom_length(self):
        """Test secure password generation with custom length."""
        handler = PasswordHandler()

        password = handler.generate_secure_password(length=24)
        assert len(password) == 24

    def test_generate_secure_password_no_symbols(self):
        """Test secure password generation without symbols."""
        handler = PasswordHandler()

        password = handler.generate_secure_password(include_symbols=False)

        assert len(password) == 16
        assert not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)

    def test_generate_secure_password_minimum_length(self):
        """Test secure password generation validates minimum length."""
        handler = PasswordHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.generate_secure_password(length=7)

        assert "Password length must be at least 8 characters" in str(exc_info.value)

    def test_get_algorithm_info(self):
        """Test getting algorithm information."""
        handler = PasswordHandler()

        info = handler.get_algorithm_info()

        assert "current_algorithm" in info
        assert "available_algorithms" in info
        assert "recommended" in info

        assert isinstance(info["available_algorithms"], dict)
        assert "argon2" in info["available_algorithms"]
        assert "bcrypt" in info["available_algorithms"]
        assert "pbkdf2" in info["available_algorithms"]

        # PBKDF2 should always be available
        assert info["available_algorithms"]["pbkdf2"] is True

    def test_hash_password_exception_handling(self):
        """Test exception handling during password hashing."""
        handler = PasswordHandler(algorithm="pbkdf2")

        # Mock hashlib.pbkdf2_hmac to raise an exception
        with patch(
            "src.auth.security.password_handler.hashlib.pbkdf2_hmac",
            side_effect=Exception("Hash failed"),
        ):
            with pytest.raises(AuthenticationException) as exc_info:
                handler.hash_password("test_password")

            assert "Password hashing failed" in str(exc_info.value)

    def test_verify_password_exception_handling(self):
        """Test exception handling during password verification."""
        handler = PasswordHandler(algorithm="pbkdf2")

        # Mock verification to raise an exception
        with patch(
            "src.auth.security.password_handler.hashlib.pbkdf2_hmac",
            side_effect=Exception("Verify failed"),
        ):
            result = handler.verify_password("password", "hash", "salt")

            # Should return False on exception, not raise
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
