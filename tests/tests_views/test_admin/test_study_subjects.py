import pytest
import json
from datetime import datetime, timezone
from aws_portal.models import Api, Study, StudySubject
from aws_portal.extensions import db
import traceback

# ===========================
# Fixtures for Initial Setup
# ===========================

@pytest.fixture(scope="function")
def create_studies(app):
    """
    Fixture to create initial studies in the database.
    """
    study1 = Study(name="Study 1", acronym="STUD1", ditti_id="D001", email="study1@example.com")
    study2 = Study(name="Study 2", acronym="STUD2", ditti_id="D002", email="study2@example.com")
    db.session.add_all([study1, study2])
    db.session.commit()
    return [study1, study2]

@pytest.fixture(scope="function")
def create_apis(app):
    """
    Fixture to create initial APIs in the database.
    """
    api1 = Api(name="API 1")
    api2 = Api(name="API 2")
    db.session.add_all([api1, api2])
    db.session.commit()
    return [api1, api2]

# ===========================
# Helper Functions
# ===========================

def get_study_entry(study_id, expires_on, did_consent):
    """
    Helper function to create a study entry for payloads.
    """
    return {
        "id": study_id,
        "expires_on": expires_on,
        "did_consent": did_consent
    }

def get_api_entry(api_id, api_user_uuid, scope, access_key_uuid, refresh_key_uuid):
    """
    Helper function to create an API entry for payloads.
    """
    return {
        "id": api_id,
        "api_user_uuid": api_user_uuid,
        "scope": scope,
        "access_key_uuid": access_key_uuid,
        "refresh_key_uuid": refresh_key_uuid
    }

@pytest.fixture
def create_study_subject(post_admin, create_studies, create_apis, app):
    """
    Fixture to create a StudySubject with customizable parameters.
    """
    def _create(email, studies=None, apis=None):
        create_data = {
            "app": 1,
            "create": {
                "email": email,
                "studies": studies or [],
                "apis": apis or []
            }
        }
        res_create = post_admin("/admin/study_subject/create", data=json.dumps(create_data))
        data_create = json.loads(res_create.data)
        assert "msg" in data_create
        assert data_create["msg"] == "Study Subject Created Successfully"
        subject = StudySubject.query.filter(StudySubject.email == email).first()
        assert subject is not None
        return subject
    return _create

def edit_study_subject(post_admin, subject_id, edit_payload):
    """
    Helper function to send an edit request and parse the response.
    """
    try:
        res_edit = post_admin("/admin/study_subject/edit", data=json.dumps(edit_payload))
        data_edit = json.loads(res_edit.data)
        return res_edit, data_edit
    except Exception as e:
        traceback.print_exc()
        pytest.fail(f"Exception during edit_study_subject: {e}")

# ===========================
# Specific Success Tests
# ===========================

def test_study_subject_create(post_admin, create_studies, create_apis):
    """
    Test creating a StudySubject with valid data.
    """
    data = {
        "app": 1,
        "create": {
            "email": "study_subject_create@example.com",
            "studies": [
                {
                    "id": 1,
                    "expires_on": "2024-12-31T23:59:59Z",
                    "did_consent": True
                }
            ],
            "apis": [
                {
                    "id": 1,
                    "api_user_uuid": "api-user-uuid-1",
                    "scope": ["read", "write"],
                    "access_key_uuid": "access-key-uuid-1",
                    "refresh_key_uuid": "refresh-key-uuid-1"
                }
            ]
        }
    }

    # Send POST request to create StudySubject
    res = post_admin("/admin/study_subject/create", data=json.dumps(data))
    data_res = json.loads(res.data)
    
    # Assert response
    assert res.status_code == 200
    assert "msg" in data_res
    assert data_res["msg"] == "Study Subject Created Successfully"

    # Query the database to verify creation
    subject = StudySubject.query.filter(StudySubject.email == "study_subject_create@example.com").first()
    assert subject is not None
    assert subject.email == "study_subject_create@example.com"
    assert not subject.is_confirmed
    assert not subject.is_archived
    assert len(subject.studies) == 1
    join_study = subject.studies[0]
    assert join_study.study_id == 1
    assert join_study.did_consent is True
    assert join_study.expires_on.replace(tzinfo=timezone.utc) == datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    assert len(subject.apis) == 1
    join_api = subject.apis[0]
    assert join_api.api_id == 1
    assert join_api.api_user_uuid == "api-user-uuid-1"
    assert join_api.scope == ["read", "write"]
    assert join_api.access_key_uuid == "access-key-uuid-1"
    assert join_api.refresh_key_uuid == "refresh-key-uuid-1"

def test_study_subject_archive(post_admin, create_study_subject, create_studies, create_apis):
    """
    Test archiving a StudySubject.
    """
    create_data = {
        "app": 1,
        "create": {
            "email": "study_subject_archive@example.com",
            "studies": [
                {
                    "id": 2,
                    "expires_on": "2025-06-30T12:00:00Z",
                    "did_consent": False
                }
            ],
            "apis": [
                {
                    "id": 2,
                    "api_user_uuid": "api-user-uuid-2",
                    "scope": ["read"],
                    "access_key_uuid": "access-key-uuid-2",
                    "refresh_key_uuid": "refresh-key-uuid-2"
                }
            ]
        }
    }

    # Create the StudySubject
    res_create = post_admin("/admin/study_subject/create", data=json.dumps(create_data))
    data_create = json.loads(res_create.data)
    assert res_create.status_code == 200
    assert "msg" in data_create
    assert data_create["msg"] == "Study Subject Created Successfully"

    # Retrieve the created StudySubject's ID
    subject = StudySubject.query.filter(StudySubject.email == "study_subject_archive@example.com").first()
    assert subject is not None
    subject_id = subject.id

    # Define the payload for archiving the StudySubject
    archive_data = {
        "app": 1,
        "id": subject_id
    }

    # Send POST request to archive StudySubject
    res_archive = post_admin("/admin/study_subject/archive", data=json.dumps(archive_data))
    data_archive = json.loads(res_archive.data)
    
    # Assert response
    assert res_archive.status_code == 200
    assert "msg" in data_archive
    assert data_archive["msg"] == "Study Subject Archived Successfully"

    # Query the database to verify archiving
    archived_subject = StudySubject.query.get(subject_id)
    assert archived_subject.is_archived is True

def test_study_subject_edit_remove_studies(post_admin, create_study_subject):
    """
    Test editing a StudySubject by removing all associated studies.
    """
    # Create a StudySubject with studies
    subject = create_study_subject(
        email="remove_studies@example.com",
        studies=[
            get_study_entry(1, "2024-12-31T23:59:59Z", True),
            get_study_entry(2, "2025-06-30T12:00:00Z", False)
        ],
        apis=[]
    )
    subject_id = subject.id

    # Define the payload to remove all studies
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "studies": []
        }
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert res_edit.status_code == 200
    assert "msg" in data_edit
    assert data_edit["msg"] == "Study Subject Edited Successfully"

    # Verify removal in the database
    edited_subject = StudySubject.query.get(subject_id)
    assert len(edited_subject.studies) == 0

def test_study_subject_edit_remove_apis(post_admin, create_study_subject):
    """
    Test editing a StudySubject by removing all associated APIs.
    """
    # Create a StudySubject with APIs
    subject = create_study_subject(
        email="remove_apis@example.com",
        studies=[],
        apis=[
            get_api_entry(1, "api-user-uuid-remove1", ["read"], "access-key-uuid-remove1", "refresh-key-uuid-remove1"),
            get_api_entry(2, "api-user-uuid-remove2", ["write"], "access-key-uuid-remove2", "refresh-key-uuid-remove2")
        ]
    )
    subject_id = subject.id

    # Define the payload to remove all APIs
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "apis": []
        }
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert res_edit.status_code == 200
    assert "msg" in data_edit
    assert data_edit["msg"] == "Study Subject Edited Successfully"

    # Verify removal in the database
    edited_subject = StudySubject.query.get(subject_id)
    assert len(edited_subject.apis) == 0

def test_study_subject_edit_invalid_scope_type(post_admin, create_study_subject):
    """
    Test editing a StudySubject with 'scope' not being a list in API association.
    """
    # Create a StudySubject to edit
    subject = create_study_subject(
        email="invalid_scope_type@example.com",
        studies=[],
        apis=[]
    )
    subject_id = subject.id

    # Define the payload with 'scope' as a string instead of a list
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "apis": [
                {
                    "id": 1,
                    "api_user_uuid": "updated-api-user-uuid",
                    "scope": "read",  # String instead of a list
                    "access_key_uuid": "updated-access-key-uuid",
                    "refresh_key_uuid": "updated-refresh-key-uuid"
                }
            ]
        }
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert "msg" in data_edit

    # Verify that 'scope' is converted to a list
    edited_subject = StudySubject.query.get(subject_id)
    assert len(edited_subject.apis) == 1
    join_api = edited_subject.apis[0]
    assert join_api.scope == ["read"]

def test_study_subject_edit_associate_existing_api(post_admin, create_study_subject):
    """
    Test editing a StudySubject by associating it with an API that is already associated.
    """
    # Create a StudySubject with an API
    subject = create_study_subject(
        email="existing_api_association@example.com",
        studies=[],
        apis=[
            get_api_entry(1, "existing-api-user-uuid", ["read"], "existing-access-key-uuid", "existing-refresh-key-uuid")
        ]
    )
    subject_id = subject.id

    # Define the payload to associate with the same API again
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "apis": [
                {
                    "id": 1,  # Already associated
                    "api_user_uuid": "updated-api-user-uuid",
                    "scope": ["read", "write"],
                    "access_key_uuid": "updated-access-key-uuid",
                    "refresh_key_uuid": "updated-refresh-key-uuid"
                }
            ]
        }
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert res_edit.status_code == 200
    assert "msg" in data_edit
    assert data_edit["msg"] == "Study Subject Edited Successfully"

    # Verify API update in the database
    edited_subject = StudySubject.query.get(subject_id)
    assert len(edited_subject.apis) == 1
    join_api = edited_subject.apis[0]
    assert join_api.api_id == 1
    assert join_api.api_user_uuid == "updated-api-user-uuid"
    assert join_api.scope == ["read", "write"]
    assert join_api.access_key_uuid == "updated-access-key-uuid"
    assert join_api.refresh_key_uuid == "updated-refresh-key-uuid"

def test_study_subject_edit_add_existing_study(post_admin, create_study_subject):
    """
    Test editing a StudySubject by adding a study that is already associated.
    """
    # Create a StudySubject with a study
    subject = create_study_subject(
        email="existing_study_add@example.com",
        studies=[
            get_study_entry(1, "2024-12-31T23:59:59Z", True)
        ],
        apis=[]
    )
    subject_id = subject.id

    # Define the payload to add the same study again
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "studies": [
                {
                    "id": 1,  # Already associated
                    "expires_on": "2025-12-31T23:59:59Z",
                    "did_consent": False
                }
            ]
        }
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert res_edit.status_code == 200
    assert "msg" in data_edit
    assert data_edit["msg"] == "Study Subject Edited Successfully"

    # Verify study update in the database
    edited_subject = StudySubject.query.get(subject_id)
    assert len(edited_subject.studies) == 1
    join_study = edited_subject.studies[0]
    assert join_study.study_id == 1
    assert join_study.did_consent is False
    assert join_study.expires_on.replace(tzinfo=timezone.utc) == datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

# ===========================
# Parameterized Success Tests
# ===========================

@pytest.mark.parametrize(
    "test_name, initial_email, edit_payload, expected_email, expected_studies, expected_apis",
    [
        (
            "Change email",
            "original_email@example.com",
            {"email": "updated_email@example.com"},
            "updated_email@example.com",
            None,  # No change to studies
            None   # No change to APIs
        ),
        (
            "Update studies",
            "study_edit_subject@example.com",
            {"studies": [
                get_study_entry(1, "2025-12-31T23:59:59Z", False),
                get_study_entry(2, "2026-06-30T12:00:00Z", True)
            ]},
            None,  # No change to email
            [
                {"study_id": 1, "did_consent": False, "expires_on": datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)},
                {"study_id": 2, "did_consent": True, "expires_on": datetime(2026, 6, 30, 12, 0, 0, tzinfo=timezone.utc)}
            ],
            None   # No change to APIs
        ),
        (
            "Update APIs",
            "api_edit_subject@example.com",
            {"apis": [
                get_api_entry(1, "updated-api-user-uuid", ["read", "write"], "updated-access-key-uuid", "updated-refresh-key-uuid"),
                get_api_entry(2, "new-api-user-uuid", ["read"], "new-access-key-uuid", "new-refresh-key-uuid")
            ]},
            None,  # No change to email
            None,  # No change to studies
            [
                {"api_id": 1, "api_user_uuid": "updated-api-user-uuid", "scope": ["read", "write"], "access_key_uuid": "updated-access-key-uuid", "refresh_key_uuid": "updated-refresh-key-uuid"},
                {"api_id": 2, "api_user_uuid": "new-api-user-uuid", "scope": ["read"], "access_key_uuid": "new-access-key-uuid", "refresh_key_uuid": "new-refresh-key-uuid"}
            ]
        ),
        (
            "Partial update",
            "partial_update@example.com",
            {"email": "partially_updated@example.com"},
            "partially_updated@example.com",
            None,  # No change to studies
            None   # No change to APIs
        ),
        (
            "No changes",
            "no_change@example.com",
            {},
            "no_change@example.com",
            None,  # No change to studies
            None   # No change to APIs
        )
    ]
)
def test_study_subject_edit_success(
    post_admin,
    create_study_subject,
    test_name,
    initial_email,
    edit_payload,
    expected_email,
    expected_studies,
    expected_apis
):
    """
    Parameterized test for successful editing of StudySubject.
    """
    # Create initial StudySubject
    initial_studies = []
    if expected_studies:
        for study in expected_studies:
            initial_studies.append({
                "id": study["study_id"],
                "expires_on": study["expires_on"].isoformat(),
                "did_consent": study["did_consent"]
            })
    initial_apis = []
    if expected_apis:
        for api in expected_apis:
            initial_apis.append({
                "id": api["api_id"],
                "api_user_uuid": api["api_user_uuid"],
                "scope": api["scope"],
                "access_key_uuid": api["access_key_uuid"],
                "refresh_key_uuid": api["refresh_key_uuid"]
            })

    subject = create_study_subject(
        email=initial_email,
        studies=initial_studies,
        apis=initial_apis
    )
    subject_id = subject.id

    # Prepare edit data
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": edit_payload
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert res_edit.status_code == 200
    assert "msg" in data_edit
    assert data_edit["msg"] == "Study Subject Edited Successfully"

    # Verify changes in the database
    edited_subject = StudySubject.query.get(subject_id)
    if expected_email:
        assert edited_subject.email == expected_email
    if expected_studies is not None:
        assert len(edited_subject.studies) == len(expected_studies)
        for study, expected in zip(edited_subject.studies, expected_studies):
            assert study.study_id == expected["study_id"]
            assert study.did_consent == expected["did_consent"]
            assert study.expires_on.replace(tzinfo=timezone.utc) == expected["expires_on"]
    if expected_apis is not None:
        assert len(edited_subject.apis) == len(expected_apis)
        for api, expected in zip(edited_subject.apis, expected_apis):
            assert api.api_id == expected["api_id"]
            assert api.api_user_uuid == expected["api_user_uuid"]
            assert api.scope == expected["scope"]
            assert api.access_key_uuid == expected["access_key_uuid"]
            assert api.refresh_key_uuid == expected["refresh_key_uuid"]

# ===========================
# Parameterized Error Tests
# ===========================

@pytest.mark.parametrize(
    "test_name, initial_email, edit_payload, expected_msg",
    [
        (
            "Missing ID",
            "missing_id@example.com",
            {"email": "new_email@example.com"},
            "Study Subject ID not provided"
        ),
        (
            "Non-existent ID",
            "nonexistent_id@example.com",
            {"id": 9999, "edit": {"email": "new_email@example.com"}},
            "Study Subject with ID 9999 does not exist"
        ),
        (
            "Duplicate Email",
            "existing_email2@example.com",
            {"email": "existing_email1@example.com"},  # Assuming "existing_email1@example.com" already exists
            "Email already exists"
        ),
        (
            "Invalid Study ID",
            "invalid_study_id@example.com",
            {"studies": [get_study_entry(9999, "2025-12-31T23:59:59Z", True)]},
            "Invalid study ID: 9999"
        ),
        (
            "Invalid API ID",
            "invalid_api_id@example.com",
            {"apis": [get_api_entry(9999, "invalid-api-user-uuid", ["read"], "invalid-access-key-uuid", "invalid-refresh-key-uuid")]},
            "Invalid API ID: 9999"
        ),
        (
            "Invalid Expires On Format",
            "invalid_expires_on@example.com",
            {"studies": [get_study_entry(1, "31-12-2024 23:59:59", True)]},  # Invalid date format
            "Invalid date format for expires_on: 31-12-2024 23:59:59"
        ),
        (
            "Missing Study ID in Study Entry",
            "missing_study_id@example.com",
            {"studies": [{"expires_on": "2025-12-31T23:59:59Z", "did_consent": True}]},  # Missing 'id'
            "Study ID is required in studies"
        ),
        (
            "Missing API ID in API Entry",
            "missing_api_id@example.com",
            {"apis": [{"api_user_uuid": "missing-api-id-uuid", "scope": ["read"], "access_key_uuid": "missing-access-key-uuid", "refresh_key_uuid": "missing-refresh-key-uuid"}]},  # Missing 'id'
            "API ID is required in apis"
        ),
        (
            "Missing api_user_uuid in API Association",
            "missing_api_user_uuid@example.com",
            {"apis": [get_api_entry(1, None, ["read"], "new-access-key-uuid", "new-refresh-key-uuid")]},  # 'api_user_uuid' is None
            "'api_user_uuid' is required for API ID 1"
        ),
        (
            "Extra Fields in Edit Payload",
            "extra_fields@example.com",
            {"studies": [], "apis": [], "unexpected_field": "unexpected_value"},
            "Invalid attribute"
        )
    ]
)
def test_study_subject_edit_errors(
    post_admin,
    create_study_subject,
    create_studies,
    create_apis,
    test_name,
    initial_email,
    edit_payload,
    expected_msg
):
    """
    Parameterized test for error scenarios during editing of StudySubject.
    """
    # Special setup for certain test cases
    if test_name == "Duplicate Email":
        # Create another StudySubject with the email to duplicate
        create_study_subject(
            email="existing_email1@example.com",
            studies=[],
            apis=[]
        )

    if test_name == "Associate Archived Study":
        # Create and archive a study with a dynamic ID
        archived_study = Study(name="Archived Study", acronym="ARCH", ditti_id="ARCH001", email="archived_study@example.com")
        archived_study.is_archived = True
        db.session.add(archived_study)
        db.session.commit()
        # Update edit_payload with the archived study ID
        edit_payload = {"studies": [get_study_entry(archived_study.id, "2025-12-31T23:59:59Z", True)]}

    if test_name == "Associate Archived API":
        # Create and archive an API with a dynamic ID
        archived_api = Api(name="Archived API")
        archived_api.is_archived = True
        db.session.add(archived_api)
        db.session.commit()
        # Update edit_payload with the archived API ID
        edit_payload = {"apis": [get_api_entry(archived_api.id, "archived-api-user-uuid", ["read"], "archived-access-key-uuid", "archived-refresh-key-uuid")]}

    # Create initial StudySubject unless test case involves missing ID or Non-existent ID
    if test_name not in ["Missing ID", "Non-existent ID", "Duplicate Email", "Associate Archived Study", "Associate Archived API"]:
        subject = create_study_subject(
            email=initial_email,
            studies=[
                get_study_entry(1, "2024-12-31T23:59:59Z", True)
            ],
            apis=[
                get_api_entry(1, "existing-api-user-uuid", ["read"], "existing-access-key-uuid", "existing-refresh-key-uuid")
            ]
        )
        subject_id = subject.id
    elif test_name == "Duplicate Email":
        # Create initial StudySubject with a different email
        subject = create_study_subject(
            email=initial_email,
            studies=[],
            apis=[]
        )
        subject_id = subject.id
    else:
        # For "Missing ID" and "Non-existent ID"
        subject_id = None

    # Prepare edit data
    if test_name == "Missing ID":
        # Exclude 'id' from the payload
        edit_data = {
            "app": 1,
            "edit": edit_payload
        }
    elif test_name == "Non-existent ID":
        # Use a non-existent ID (assuming 9999 does not exist)
        edit_data = {
            "app": 1,
            "id": 9999,  # Ensured to be non-existent
            "edit": edit_payload
        }
    elif test_name == "Associate Archived Study" or test_name == "Associate Archived API":
        # Use the dynamically assigned archived study/API ID
        edit_data = {
            "app": 1,
            "id": subject_id if subject_id else 0,  # Adjust as needed
            "edit": edit_payload
        }
    else:
        # Use the created subject's ID
        edit_data = {
            "app": 1,
            "id": subject_id,
            "edit": edit_payload
        }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id if subject_id else 0, edit_data)

    # Assert response based on test case
    if test_name == "Missing ID":
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg
    elif test_name == "Non-existent ID":
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg
    elif test_name == "Duplicate Email":
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg
    elif test_name == "Associate Archived Study":
        # Expecting an error related to the archived study
        archived_study_id = edit_payload["studies"][0]["id"]
        expected_msg_dynamic = f"Cannot associate with archived study ID: {archived_study_id}"
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg_dynamic
    elif test_name == "Associate Archived API":
        # Expecting an error related to the archived API
        archived_api_id = edit_payload["apis"][0]["id"]
        expected_msg_dynamic = f"Cannot associate with archived API ID: {archived_api_id}"
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg_dynamic
    elif test_name == "Extra Fields in Edit Payload":
        assert res_edit.status_code == 500
        assert "msg" in data_edit
        assert expected_msg in data_edit["msg"]
    else:
        # General error cases
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg