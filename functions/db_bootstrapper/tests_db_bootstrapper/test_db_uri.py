from urllib.parse import quote_plus

import pytest
from src.db_uri import DbUri


class TestDbUri:
    """Test cases for the DbUri class."""

    def test_init_without_password(self):
        """Test DbUri initialization without password."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
        )

        assert db_uri.uri == "postgresql://testuser@localhost:5432/testdb"
        assert db_uri.has_password is False
        assert db_uri.hostname == "localhost"
        assert db_uri.port == 5432
        assert db_uri.database == "testdb"
        assert db_uri.username == "testuser"

    def test_init_with_password(self):
        """Test DbUri initialization with password."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
            password="testpass",
        )

        assert (
            db_uri.uri == "postgresql://testuser:testpass@localhost:5432/testdb"
        )
        assert db_uri.has_password is True
        assert db_uri.hostname == "localhost"
        assert db_uri.port == 5432
        assert db_uri.database == "testdb"
        assert db_uri.username == "testuser"

    def test_init_with_none_password(self):
        """Test DbUri initialization with explicit None password."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
            password=None,
        )

        assert db_uri.uri == "postgresql://testuser@localhost:5432/testdb"
        assert db_uri.has_password is False

    def test_port_conversion_to_int(self):
        """Test that port is converted to integer."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
        )

        assert isinstance(db_uri.port, int)
        assert db_uri.port == 5432

    def test_password_with_special_characters(self):
        """Test password URL encoding for special characters."""
        special_password = "pass@word:123"
        encoded_password = quote_plus(special_password)

        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
            password=special_password,
        )

        expected_uri = (
            f"postgresql://testuser:{encoded_password}@localhost:5432/testdb"
        )
        assert db_uri.uri == expected_uri
        assert db_uri.has_password is True

    @pytest.mark.parametrize(
        "password", ["user@domain.com", "pass:word", "pass/word", "pässwörd"]
    )
    def test_password_with_special_symbols(self, password: str):
        """Test password containing @ symbol."""
        encoded_password = quote_plus(password)

        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
            password=password,
        )

        expected_uri = (
            f"postgresql://testuser:{encoded_password}@localhost:5432/testdb"
        )
        assert db_uri.uri == expected_uri

    def test_str_representation_without_password(self):
        """Test string representation without password."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
        )

        expected_str = "postgresql://testuser@localhost:5432/testdb"
        assert str(db_uri) == expected_str

    def test_str_representation_with_password(self):
        """Test string representation with password (should mask password)."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
            password="secretpass",
        )

        expected_str = "postgresql://testuser:***@localhost:5432/testdb"
        assert str(db_uri) == expected_str

    def test_str_representation_with_encoded_password(self):
        """Test string representation with encoded password (should still mask password)."""
        db_uri = DbUri(
            hostname="localhost",
            port="5432",
            database="testdb",
            username="testuser",
            password="pass@word:123",
        )

        expected_str = "postgresql://testuser:***@localhost:5432/testdb"
        assert str(db_uri) == expected_str

    def test_complex_hostname(self):
        """Test with complex hostname."""
        db_uri = DbUri(
            hostname="db.example.com",
            port="5432",
            database="production_db",
            username="admin",
        )

        assert (
            db_uri.uri == "postgresql://admin@db.example.com:5432/production_db"
        )
        assert db_uri.hostname == "db.example.com"

    def test_different_port(self):
        """Test with different port number."""
        db_uri = DbUri(
            hostname="localhost",
            port="5433",
            database="testdb",
            username="testuser",
        )

        assert db_uri.port == 5433
        assert db_uri.uri == "postgresql://testuser@localhost:5433/testdb"

    def test_empty_strings(self):
        """Test with empty strings for non-critical fields."""
        db_uri = DbUri(hostname="", port="5432", database="", username="")

        assert db_uri.uri == "postgresql://@:5432/"
        assert db_uri.hostname == ""
        assert db_uri.database == ""
        assert db_uri.username == ""
