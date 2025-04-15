import pytest

from install_scripts.utils.utils import is_valid_name, is_valid_email


class TestIsValidName:
    @pytest.mark.parametrize("name", [
        "my-project",
        "my_project",
        "project123",
        "Project-123",
        "a" * 64,  # Maximum length
    ])
    def test_valid_names(self, name):
        """Test various valid project names."""
        assert is_valid_name(name) is True

    @pytest.mark.parametrize("name", [
        "",  # Empty string
        None,  # None value
        "my/project",  # Contains forward slash
        "my.project",  # Contains dot
        "my project",  # Contains space
        "my@project",  # Contains special character
        "a" * 65,  # Too long
        "My Project!",  # Contains space and special character
    ])
    def test_invalid_names(self, name):
        """Test various invalid project names."""
        assert is_valid_name(name) is False


class TestIsValidEmail:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "user.name@example.com",
        "user+label@example.com",
        "user@subdomain.example.com",
        "user@example.co.uk",
        "user123@example.com",
        "user@example.org",
    ])
    def test_valid_emails(self, email):
        """Test various valid email addresses."""
        assert is_valid_email(email) is True

    @pytest.mark.parametrize("email", [
        "",  # Empty string
        None,  # None value
        "user@",  # Missing domain
        "@example.com",  # Missing local part
        "user@example",  # Missing TLD
        "user@.com",  # Missing domain name
        "user@example.",  # Missing TLD
        "user@example..com",  # Double dot
        "user@example@example.com",  # Multiple @ symbols
        "user@example.com.",  # Trailing dot
        "user@example.c",  # TLD too short
    ])
    def test_invalid_emails(self, email):
        """Test various invalid email addresses."""
        assert is_valid_email(email) is False
