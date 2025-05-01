import pytest

from install.utils.utils import is_valid_email, is_valid_name


@pytest.mark.parametrize(
    "name",
    [
        "my-project",
        "my_project",
        "project123",
        "a" * 64,
    ],
)
def test_valid_names(name):
    """Test various valid project names."""
    assert is_valid_name(name) is True


@pytest.mark.parametrize(
    "name",
    [
        "",
        None,
        "my/project",
        "my.project",
        "my project",
        "my@project",
        "a" * 65,
        "My Project!",
        "Project-123",
    ],
)
def test_invalid_names(name):
    """Test various invalid project names."""
    assert is_valid_name(name) is False


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "user.name@example.com",
        "user+label@example.com",
        "user@subdomain.example.com",
        "user@example.co.uk",
        "user123@example.com",
        "user@example.org",
    ],
)
def test_valid_emails(email):
    """Test various valid email addresses."""
    assert is_valid_email(email) is True


@pytest.mark.parametrize(
    "email",
    [
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
    ],
)
def test_invalid_emails(email):
    """Test various invalid email addresses."""
    assert is_valid_email(email) is False
