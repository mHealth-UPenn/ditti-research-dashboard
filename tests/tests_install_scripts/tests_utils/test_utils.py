import pytest

from install_scripts.utils.utils import is_valid_name, is_valid_email


@pytest.mark.parametrize("name", [
    "my-project",
    "my_project",
    "project123",
    "Project-123",
    "a" * 64,  # Maximum length
])
def test_valid_names(name):
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
def test_invalid_names(name):
    """Test various invalid project names."""
    assert is_valid_name(name) is False


@pytest.mark.parametrize("email", [
    "user@example.com",
    "user.name@example.com",
    "user+label@example.com",
    "user@subdomain.example.com",
    "user@example.co.uk",
    "user123@example.com",
    "user@example.org",
])
def test_valid_emails(email):
    """Test various valid email addresses."""
    assert is_valid_email(email) is True


@pytest.mark.parametrize("email", [
    "",
    None,
    "user@",
    "@example.com",
    "user@example",
    "user@.com",
    "user@example.",
    "user@example..com",
    "user@example@example.com",
    "user@example.com.",
    "user@example.c",
])
def test_invalid_emails(email):
    """Test various invalid email addresses."""
    assert is_valid_email(email) is False
