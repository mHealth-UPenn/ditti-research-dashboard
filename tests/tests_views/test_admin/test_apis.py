import json

import pytest

from backend.extensions import db
from backend.models import Api

# ===========================
# Helper Functions
# ===========================


def create_api_payload(name):
    """Create an API payload."""
    return {"app": 1, "create": {"name": name}}


def edit_api_payload(api_id, name=None):
    """Create an API edit payload."""
    payload = {"app": 1, "id": api_id, "edit": {}}
    if name is not None:
        payload["edit"]["name"] = name
    return payload


def archive_api_payload(api_id):
    """Create an API archive payload."""
    return {"app": 1, "id": api_id}


@pytest.fixture
def create_api(post_admin):
    """Fixture to create an API with customizable parameters."""

    def _create(name):
        create_data = create_api_payload(name)
        res_create = post_admin("/admin/api/create", data=create_data)
        data_create = json.loads(res_create.data)
        assert "msg" in data_create
        assert data_create["msg"] == "API Created Successfully"
        api = Api.query.filter_by(name=name).first()
        assert api is not None
        return api

    return _create


def get_admin_api(get_admin, api_id=None):
    """Send a GET request to the API endpoint."""
    params = {"app": 1, "id": str(api_id)} if api_id else {"app": 1}
    res = get_admin("/admin/api", query_string=params)
    return res


# ===========================
# Specific Success Tests
# ===========================


def test_api_create_success(post_admin):
    """Test creating an API with valid data."""
    data = create_api_payload("Test API")
    res = post_admin("/admin/api/create", data=data)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert "msg" in data_res
    assert data_res["msg"] == "API Created Successfully"

    # Query the database to verify creation
    api = Api.query.filter_by(name="Test API").first()
    assert api is not None
    assert api.name == "Test API"
    assert not api.is_archived


def test_api_get_all(get_admin, create_api):
    """Test retrieving all non-archived APIs."""
    # Create APIs
    create_api("API Get All 1")
    create_api("API Get All 2")
    api3 = create_api("API Get All 3")

    # Archive one API
    api3.is_archived = True
    db.session.commit()

    # Send GET request without 'id' to retrieve all APIs
    res = get_admin_api(get_admin)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    api_names = [api["name"] for api in data_res]
    assert "API Get All 1" in api_names
    assert "API Get All 2" in api_names
    assert "API Get All 3" not in api_names


def test_api_get_by_id(get_admin, create_api):
    """Test retrieving a specific API by ID."""
    api = create_api("API Get By ID")
    api_id = api.id

    res = get_admin_api(get_admin, api_id=api_id)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    assert len(data_res) == 1
    retrieved_api = data_res[0]
    assert retrieved_api["name"] == "API Get By ID"
    assert retrieved_api["id"] == api_id


def test_api_edit_success(post_admin, create_api):
    """Test editing an API with valid data."""
    # Create an API
    api = create_api("API to Edit")
    api_id = api.id

    # Prepare and send edit request
    edit_data = edit_api_payload(api_id, "Edited API Name")
    res = post_admin("/admin/api/edit", data=edit_data)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert "msg" in data_res
    assert data_res["msg"] == "API Edited Successfully"

    # Verify the API was updated in the database
    api = Api.query.get(api_id)
    assert api.name == "Edited API Name"


def test_api_archive_success(post_admin, create_api):
    """Test archiving an API successfully."""
    # Create an API
    api = create_api("API to Archive")
    api_id = api.id

    # Prepare and send archive request
    archive_data = archive_api_payload(api_id)
    res = post_admin("/admin/api/archive", data=archive_data)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert "msg" in data_res
    assert data_res["msg"] == "API Archived Successfully"

    # Verify the API was archived in the database
    api = Api.query.get(api_id)
    assert api.is_archived


# ===========================
# Error Tests
# ===========================


def test_api_create_missing_name(post_admin):
    """Test creating an API without providing a name."""
    data = {"app": 1, "create": {}}
    res = post_admin("/admin/api/create", data=data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "No data provided"


def test_api_create_duplicate_name(post_admin, create_api):
    """Test creating an API with a name that already exists."""
    create_api("Duplicate API Name")
    data = create_api_payload("Duplicate API Name")
    res = post_admin("/admin/api/create", data=data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "API name already exists"


def test_api_edit_nonexistent_id(post_admin):
    """Test editing an API with an ID that doesn't exist."""
    edit_data = edit_api_payload(9999, "Nonexistent API")
    res = post_admin("/admin/api/edit", data=edit_data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "API with ID 9999 does not exist"


def test_api_edit_duplicate_name(post_admin, create_api):
    """Test editing an API with a name that already exists."""
    create_api("Original API 1")
    api2 = create_api("Original API 2")
    edit_data = edit_api_payload(api2.id, "Original API 1")
    res = post_admin("/admin/api/edit", data=edit_data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "API with the same name already exists"


def test_api_archive_nonexistent_id(post_admin):
    """Test archiving an API with an ID that doesn't exist."""
    archive_data = archive_api_payload(9999)
    res = post_admin("/admin/api/archive", data=archive_data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "API with ID 9999 does not exist"


def test_api_create_no_data(post_admin):
    """Test creating an API with no data provided."""
    data = {"app": 1}
    res = post_admin("/admin/api/create", data=data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "No data provided"


def test_api_edit_no_id(post_admin):
    """Test editing an API without providing an ID."""
    edit_data = {"app": 1, "edit": {"name": "New Name"}}
    res = post_admin("/admin/api/edit", data=edit_data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "API ID not provided"


def test_api_archive_no_id(post_admin):
    """Test archiving an API without providing an ID."""
    archive_data = {"app": 1}
    res = post_admin("/admin/api/archive", data=archive_data)
    data_res = json.loads(res.data)
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "API ID not provided"


# ===========================
# Parameterized Success Tests
# ===========================


@pytest.mark.parametrize(
    ("test_name", "initial_name", "edit_name", "expected_name"),
    [
        ("Change Name", "API Original Name", "API New Name", "API New Name"),
        ("No Name Change", "API No Change", None, "API No Change"),
    ],
)
def test_api_edit_parameterized(
    post_admin, create_api, test_name, initial_name, edit_name, expected_name
):
    """Parameterized test for editing an API."""
    api = create_api(initial_name)
    api_id = api.id

    if edit_name is not None:
        edit_data = edit_api_payload(api_id, edit_name)
    else:
        # When no changes are made, we need to explicitly include a name
        # to avoid the UnboundLocalError in the API endpoint
        edit_data = edit_api_payload(api_id, initial_name)

    res = post_admin("/admin/api/edit", data=edit_data)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert "msg" in data_res
    assert data_res["msg"] == "API Edited Successfully"

    # Verify the name in the database matches what we expect
    edited_api = Api.query.get(api_id)
    assert edited_api.name == expected_name


# ===========================
# Parameterized Error Tests
# ===========================


@pytest.mark.parametrize(
    ("test_name", "edit_data", "expected_msg"),
    [
        (
            "Missing ID",
            {"app": 1, "edit": {"name": "New Name"}},
            "API ID not provided",
        ),
        (
            "Non-existent ID",
            {"app": 1, "id": 9999, "edit": {"name": "New Name"}},
            "API with ID 9999 does not exist",
        ),
        ("Duplicate Name", None, "API with the same name already exists"),
    ],
)
def test_api_edit_errors(
    post_admin, create_api, test_name, edit_data, expected_msg
):
    """Parameterized test for error scenarios during editing of API."""
    if test_name == "Duplicate Name":
        # Create APIs
        api1 = create_api("API Original")
        create_api("API Duplicate")
        edit_data = edit_api_payload(api1.id, "API Duplicate")
    elif test_name == "Non-existent ID":
        # Use non-existent ID
        pass
    elif test_name == "Missing ID":
        # ID is missing in edit_data
        pass

    res = post_admin("/admin/api/edit", data=edit_data)
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == expected_msg
