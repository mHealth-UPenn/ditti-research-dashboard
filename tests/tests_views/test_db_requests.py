import json
import pytest
from tests.testing_utils import mock_researcher_auth_for_testing
from unittest.mock import patch, MagicMock


@pytest.fixture
def researcher_headers(client):
    """Fixture providing researcher authentication headers"""
    return mock_researcher_auth_for_testing(client, is_admin=False)


@pytest.fixture
def researcher_get(client, researcher_headers):
    """Create a test GET request function with researcher authentication"""
    def _get(url, query_string=None, **kwargs):
        return client.get(url, query_string=query_string, headers=researcher_headers, **kwargs)
    return _get


def test_apps(researcher_get):
    res = researcher_get("/db/get-apps")
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]["name"] == "foo"


def test_apps_admin(get_admin):
    """
    Test that admin users can access the admin dashboard app.

    This test may need to be adjusted if the app names don't match
    what's expected in the actual database.
    """
    with patch("aws_portal.models.App.query") as mock_query:
        # Mock the query to return an app with name "Admin Dashboard"
        mock_app = MagicMock()
        mock_app.meta = {"name": "Admin Dashboard"}
        mock_query.join.return_value.join.return_value.filter.return_value.all.return_value = [
            mock_app]

        res = get_admin("/db/get-apps")
        res = json.loads(res.data)
        assert len(res) == 1
        assert res[0]["name"] == "Admin Dashboard"


def test_studies(researcher_get):
    opts = "?app=2"
    res = researcher_get("/db/get-studies" + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]["name"] == "foo"


def test_study_details(researcher_get):
    opts = "?app=2&study=1"
    res = researcher_get("/db/get-study-details" + opts)
    res = json.loads(res.data)
    assert "name" in res
    assert res["name"] == "foo"
    assert "acronym" in res
    assert "dittiId" in res


def test_study_details_invalid_study(researcher_get):
    opts = "?app=2&study=2"
    res = researcher_get("/db/get-study-details" + opts)
    res = json.loads(res.data)
    assert res == {}


def test_study_contacts(researcher_get):
    opts = "?app=2&study=1"
    res = researcher_get("/db/get-study-contacts" + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert "fullName" in res[0]
    assert res[0]["fullName"] == "John Smith"
    assert "role" in res[0]
    assert res[0]["role"] == "foo"


def test_study_contacts_invalid_study(researcher_get):
    opts = "?app=2&study=2"
    res = researcher_get("/db/get-study-contacts" + opts)
    res = json.loads(res.data)
    assert len(res) == 0


def test_account_details(researcher_get):
    res = researcher_get("/db/get-account-details")
    res = json.loads(res.data)
    assert "firstName" in res
    assert res["firstName"] == "John"


def test_get_about_sleep_templates(researcher_get):
    """Test the endpoint to get about sleep templates with app parameter"""
    with patch("aws_portal.models.AboutSleepTemplate.query") as mock_query:
        # Mock the query to return a template
        mock_template = MagicMock()
        mock_template.meta = {"name": "Test Template",
                              "content": "Sample content"}
        mock_query.filter.return_value.all.return_value = [mock_template]

        # Make the request with app parameter
        res = researcher_get("/db/get-about-sleep-templates?app=2")
        assert res.status_code == 200

        data = json.loads(res.data)
        assert len(data) == 1
        assert data[0]["name"] == "Test Template"
        assert data[0]["content"] == "Sample content"
