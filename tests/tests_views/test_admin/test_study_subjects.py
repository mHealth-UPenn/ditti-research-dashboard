import pytest
import json
from datetime import datetime, timezone
from aws_portal.models import Api, Study, StudySubject
from aws_portal.extensions import db
import traceback

# Years to use for setting expiry dates
year = datetime.now().year + 1
next_year = datetime.now().year + 2
next_next_year = datetime.now().year + 3


# ===========================
# Fixtures for Initial Setup
# ===========================


@pytest.fixture(scope="function")
def create_studies(app):
    """
    Fixture to create initial studies in the database.
    """
    study1 = Study(
        name="Study 1",
        acronym="STUD1",
        ditti_id="D001",
        email="study1@example.com",
        default_expiry_delta=30,
    )
    study2 = Study(
        name="Study 2",
        acronym="STUD2",
        ditti_id="D002",
        email="study2@example.com",
        default_expiry_delta=30,
    )
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
    entry = {
        "id": study_id,
        "did_consent": did_consent,
    }
    if expires_on is not None:
        entry["expires_on"] = expires_on
    return entry


def get_api_entry(api_id, api_user_uuid, scope):
    """
    Helper function to create an API entry for payloads.
    """
    return {
        "id": api_id,
        "api_user_uuid": api_user_uuid,
        "scope": scope,
    }


@pytest.fixture
def create_study_subject(post_admin, create_studies, create_apis, app):
    """
    Fixture to create a StudySubject with customizable parameters.
    """
    def _create(ditti_id, studies=None, apis=None):
        create_data = {
            "app": 1,
            "create": {
                "ditti_id": ditti_id,
                "studies": studies or [],
                "apis": apis or [],
            },
        }
        res_create = post_admin(
            "/admin/study_subject/create", data=json.dumps(create_data)
        )
        data_create = json.loads(res_create.data)
        assert "msg" in data_create
        assert data_create["msg"] == "Study Subject Created Successfully"
        subject = StudySubject.query.filter(
            StudySubject.ditti_id == ditti_id
        ).first()
        assert subject is not None
        return subject
    return _create


def edit_study_subject(post_admin, subject_id, edit_payload):
    """
    Helper function to send an edit request and parse the response.
    """
    try:
        res_edit = post_admin(
            "/admin/study_subject/edit", data=json.dumps(edit_payload)
        )
        data_edit = json.loads(res_edit.data)
        return res_edit, data_edit
    except Exception as e:
        traceback.print_exc()
        pytest.fail(f"Exception during edit_study_subject: {e}")


def get_admin_study_subject(get_admin, study_subject_id=None):
    """
    Helper function to send a GET request to the study_subject endpoint.
    """
    if study_subject_id:
        params = {"app": 1, "id": str(study_subject_id)}
    else:
        params = {"app": 1}
    res = get_admin("/admin/study_subject", query_string=params)
    return res

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
            "ditti_id": "study_subject_create_ditti_id",
            "studies": [
                {
                    "id": 1,
                    "expires_on": f"{year}-12-31T23:59:59Z",
                    "did_consent": True,
                }
            ],
            "apis": [
                {
                    "id": 1,
                    "api_user_uuid": "api-user-uuid-1",
                    "scope": ["read", "write"],
                }
            ],
        },
    }

    # Send POST request to create StudySubject
    res = post_admin("/admin/study_subject/create", data=json.dumps(data))
    data_res = json.loads(res.data)

    # Assert response
    assert res.status_code == 200
    assert "msg" in data_res
    assert data_res["msg"] == "Study Subject Created Successfully"

    # Query the database to verify creation
    subject = StudySubject.query.filter(
        StudySubject.ditti_id == "study_subject_create_ditti_id"
    ).first()
    assert subject is not None
    assert subject.ditti_id == "study_subject_create_ditti_id"
    assert not subject.is_archived
    assert len(subject.studies) == 1
    join_study = subject.studies[0]
    assert join_study.study_id == 1
    assert join_study.did_consent is True
    assert join_study.expires_on.replace(tzinfo=timezone.utc) == datetime(
        year, 12, 31, 23, 59, 59, tzinfo=timezone.utc
    )
    assert len(subject.apis) == 1
    join_api = subject.apis[0]
    assert join_api.api_id == 1
    assert join_api.api_user_uuid == "api-user-uuid-1"
    assert join_api.scope == ["read", "write"]


def test_study_subject_archive(
    post_admin, create_study_subject, create_studies, create_apis
):
    """
    Test archiving a StudySubject.
    """
    create_data = {
        "app": 1,
        "create": {
            "ditti_id": "study_subject_archive_ditti_id",
            "studies": [
                {
                    "id": 2,
                    "expires_on": f"{next_year}-06-30T12:00:00Z",
                    "did_consent": False,
                }
            ],
            "apis": [
                {
                    "id": 2,
                    "api_user_uuid": "api-user-uuid-2",
                    "scope": ["read"],
                }
            ],
        },
    }

    # Create the StudySubject
    res_create = post_admin(
        "/admin/study_subject/create", data=json.dumps(create_data)
    )
    data_create = json.loads(res_create.data)
    assert res_create.status_code == 200
    assert "msg" in data_create
    assert data_create["msg"] == "Study Subject Created Successfully"

    # Retrieve the created StudySubject's ID
    subject = StudySubject.query.filter(
        StudySubject.ditti_id == "study_subject_archive_ditti_id"
    ).first()
    assert subject is not None
    subject_id = subject.id

    # Define the payload for archiving the StudySubject
    archive_data = {
        "app": 1,
        "id": subject_id,
    }

    # Send POST request to archive StudySubject
    res_archive = post_admin(
        "/admin/study_subject/archive", data=json.dumps(archive_data)
    )
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
        ditti_id="remove_studies_ditti_id",
        studies=[
            get_study_entry(1, f"{year}-12-31T23:59:59Z", True),
            get_study_entry(2, f"{next_year}-06-30T12:00:00Z", False),
        ],
        apis=[],
    )
    subject_id = subject.id

    # Define the payload to remove all studies
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "studies": [],
        },
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
        ditti_id="remove_apis_ditti_id",
        studies=[],
        apis=[
            get_api_entry(1, "api-user-uuid-remove1", ["read"]),
            get_api_entry(2, "api-user-uuid-remove2", ["write"]),
        ],
    )
    subject_id = subject.id

    # Define the payload to remove all APIs
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": {
            "apis": [],
        },
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
        ditti_id="invalid_scope_type_ditti_id",
        studies=[],
        apis=[],
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
                }
            ],
        },
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
        ditti_id="existing_api_association_ditti_id",
        studies=[],
        apis=[
            get_api_entry(1, "existing-api-user-uuid", ["read"]),
        ],
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
                }
            ],
        },
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


def test_study_subject_edit_add_existing_study(post_admin, create_study_subject):
    """
    Test editing a StudySubject by adding a study that is already associated.
    """
    # Create a StudySubject with a study
    subject = create_study_subject(
        ditti_id="existing_study_add_ditti_id",
        studies=[
            get_study_entry(1, f"{year}-12-31T23:59:59Z", True),
        ],
        apis=[],
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
                    "expires_on": f"{next_year}-12-31T23:59:59Z",
                    "did_consent": False,
                }
            ],
        },
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
    assert join_study.expires_on.replace(tzinfo=timezone.utc) == datetime(
        next_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc
    )

# ===========================
# Parameterized Success Tests
# ===========================


@pytest.mark.parametrize(
    "test_name, initial_ditti_id, edit_payload, expected_ditti_id, expected_studies, expected_apis",
    [
        (
            "Change ditti_id",
            "original_ditti_id",
            {"ditti_id": "updated_ditti_id"},
            "updated_ditti_id",
            None,  # No change to studies
            None,  # No change to APIs
        ),
        (
            "Update studies",
            "study_edit_subject_ditti_id",
            {
                "studies": [
                    get_study_entry(1, f"{next_year}-12-31T23:59:59Z", False),
                    get_study_entry(2, f"{next_next_year}-06-30T12:00:00Z", True),
                ]
            },
            None,  # No change to ditti_id
            [
                {
                    "study_id": 1,
                    "did_consent": False,
                    "expires_on": datetime(
                        next_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc
                    ),
                },
                {
                    "study_id": 2,
                    "did_consent": True,
                    "expires_on": datetime(
                        next_next_year, 6, 30, 12, 0, 0, tzinfo=timezone.utc
                    ),
                },
            ],
            None,  # No change to APIs
        ),
        (
            "Update APIs",
            "api_edit_subject_ditti_id",
            {
                "apis": [
                    get_api_entry(1, "updated-api-user-uuid",
                                  ["read", "write"]),
                    get_api_entry(2, "new-api-user-uuid", ["read"]),
                ]
            },
            None,  # No change to ditti_id
            None,  # No change to studies
            [
                {
                    "api_id": 1,
                    "api_user_uuid": "updated-api-user-uuid",
                    "scope": ["read", "write"],
                },
                {
                    "api_id": 2,
                    "api_user_uuid": "new-api-user-uuid",
                    "scope": ["read"],
                },
            ],
        ),
        (
            "Partial update",
            "partial_update_ditti_id",
            {"ditti_id": "partially_updated_ditti_id"},
            "partially_updated_ditti_id",
            None,  # No change to studies
            None,  # No change to APIs
        ),
        (
            "No changes",
            "no_change_ditti_id",
            {},
            "no_change_ditti_id",
            None,  # No change to studies
            None,  # No change to APIs
        ),
    ],
)
def test_study_subject_edit_success(
    post_admin,
    create_study_subject,
    test_name,
    initial_ditti_id,
    edit_payload,
    expected_ditti_id,
    expected_studies,
    expected_apis,
):
    """
    Parameterized test for successful editing of StudySubject.
    """
    # Create initial StudySubject
    initial_studies = []
    if expected_studies:
        for study in expected_studies:
            initial_studies.append(
                {
                    "id": study["study_id"],
                    "expires_on": study["expires_on"].isoformat(),
                    "did_consent": study["did_consent"],
                }
            )
    initial_apis = []
    if expected_apis:
        for api in expected_apis:
            initial_apis.append(
                {
                    "id": api["api_id"],
                    "api_user_uuid": api["api_user_uuid"],
                    "scope": api["scope"],
                }
            )

    subject = create_study_subject(
        ditti_id=initial_ditti_id,
        studies=initial_studies,
        apis=initial_apis,
    )
    subject_id = subject.id

    # Prepare edit data
    edit_data = {
        "app": 1,
        "id": subject_id,
        "edit": edit_payload,
    }

    # Send edit request
    res_edit, data_edit = edit_study_subject(post_admin, subject_id, edit_data)

    # Assert response
    assert res_edit.status_code == 200
    assert "msg" in data_edit
    assert data_edit["msg"] == "Study Subject Edited Successfully"

    # Verify changes in the database
    edited_subject = StudySubject.query.get(subject_id)
    if expected_ditti_id:
        assert edited_subject.ditti_id == expected_ditti_id
    if expected_studies is not None:
        assert len(edited_subject.studies) == len(expected_studies)
        for study, expected in zip(edited_subject.studies, expected_studies):
            assert study.study_id == expected["study_id"]
            assert study.did_consent == expected["did_consent"]
            assert study.expires_on.replace(
                tzinfo=timezone.utc
            ) == expected["expires_on"]
    if expected_apis is not None:
        assert len(edited_subject.apis) == len(expected_apis)
        for api, expected in zip(edited_subject.apis, expected_apis):
            assert api.api_id == expected["api_id"]
            assert api.api_user_uuid == expected["api_user_uuid"]
            assert api.scope == expected["scope"]

# ===========================
# Parameterized Error Tests
# ===========================


@pytest.mark.parametrize(
    "test_name, initial_ditti_id, edit_payload, expected_msg",
    [
        (
            "Missing ID",
            "missing_id_ditti_id",
            {"ditti_id": "new_ditti_id"},
            "Study Subject ID not provided",
        ),
        (
            "Non-existent ID",
            "nonexistent_id_ditti_id",
            {"id": 9999, "edit": {"ditti_id": "new_ditti_id"}},
            "Study Subject with ID 9999 does not exist",
        ),
        (
            "Duplicate ditti_id",
            "existing_ditti_id2",
            # Assuming "existing_ditti_id1" already exists
            {"ditti_id": "existing_ditti_id1"},
            "ditti_id already exists",
        ),
        (
            "Invalid Study ID",
            "invalid_study_id_ditti_id",
            {"studies": [get_study_entry(9999, f"{next_year}-12-31T23:59:59Z", True)]},
            "Invalid study ID: 9999",
        ),
        (
            "Invalid API ID",
            "invalid_api_id_ditti_id",
            {"apis": [get_api_entry(9999, "invalid-api-user-uuid", ["read"])]},
            "Invalid API ID: 9999",
        ),
        (
            "Invalid Expires On Format",
            "invalid_expires_on_ditti_id",
            # Invalid date format
            {"studies": [get_study_entry(1, "31-12-2024 23:59:59", True)]},
            "Invalid date format for expires_on: 31-12-2024 23:59:59",
        ),
        (
            "Missing Study ID in Study Entry",
            "missing_study_id_ditti_id",
            # Missing 'id'
            {"studies": [
                {"expires_on": f"{next_year}-12-31T23:59:59Z", "did_consent": True}]},
            "Study ID is required in studies",
        ),
        (
            "Missing API ID in API Entry",
            "missing_api_id_ditti_id",
            # Missing 'id'
            {"apis": [{"api_user_uuid": "missing-api-id-uuid", "scope": ["read"]}]},
            "API ID is required in apis",
        ),
        (
            "Missing api_user_uuid in API Association",
            "missing_api_user_uuid_ditti_id",
            # 'api_user_uuid' is None
            {"apis": [get_api_entry(1, None, ["read"])]},
            "'api_user_uuid' is required for API ID 1",
        ),
        (
            "Extra Fields in Edit Payload",
            "extra_fields_ditti_id",
            {"studies": [], "apis": [], "unexpected_field": "unexpected_value"},
            "Internal server error when editing study subject"
        )
    ]
)
def test_study_subject_edit_errors(
    post_admin,
    create_study_subject,
    create_studies,
    create_apis,
    test_name,
    initial_ditti_id,
    edit_payload,
    expected_msg,
):
    """
    Parameterized test for error scenarios during editing of StudySubject.
    """
    # Special setup for certain test cases
    if test_name == "Duplicate ditti_id":
        # Create another StudySubject with the ditti_id to duplicate
        create_study_subject(
            ditti_id="existing_ditti_id1",
            studies=[],
            apis=[],
        )

    if test_name == "Associate Archived Study":
        # Create and archive a study with a dynamic ID
        archived_study = Study(
            name="Archived Study",
            acronym="ARCH",
            ditti_id="ARCH001",
            email="archived_study@example.com",
            default_expiry_delta=45,
        )
        archived_study.is_archived = True
        db.session.add(archived_study)
        db.session.commit()
        # Update edit_payload with the archived study ID
        edit_payload = {"studies": [get_study_entry(
            archived_study.id, f"{next_year}-12-31T23:59:59Z", True)]}

    if test_name == "Associate Archived API":
        # Create and archive an API with a dynamic ID
        archived_api = Api(name="Archived API")
        archived_api.is_archived = True
        db.session.add(archived_api)
        db.session.commit()
        # Update edit_payload with the archived API ID
        edit_payload = {"apis": [get_api_entry(
            archived_api.id, "archived-api-user-uuid", ["read"])]}

    # Create initial StudySubject unless test case involves missing ID or Non-existent ID
    if test_name not in ["Missing ID", "Non-existent ID", "Duplicate ditti_id", "Associate Archived Study", "Associate Archived API"]:
        subject = create_study_subject(
            ditti_id=initial_ditti_id,
            studies=[
                get_study_entry(1, f"{year}-12-31T23:59:59Z", True)
            ],
            apis=[
                get_api_entry(1, "existing-api-user-uuid", ["read"])
            ]
        )
        subject_id = subject.id
    elif test_name == "Duplicate ditti_id":
        # Create initial StudySubject with a different ditti_id
        subject = create_study_subject(
            ditti_id=initial_ditti_id,
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
    elif test_name in ["Associate Archived Study", "Associate Archived API"]:
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
    res_edit, data_edit = edit_study_subject(
        post_admin, subject_id if subject_id else 0, edit_data)

    # Assert response based on test case
    if test_name == "Missing ID":
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg
    elif test_name == "Non-existent ID":
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg
    elif test_name == "Duplicate ditti_id":
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg
    elif test_name == "Associate Archived Study":
        # Expecting an error related to the archived study
        archived_study_id = edit_payload["studies"][0]["id"]
        expected_msg_dynamic = f"Cannot associate with archived study ID: {
            archived_study_id}"
        assert res_edit.status_code == 400
        assert "msg" in data_edit
        assert data_edit["msg"] == expected_msg_dynamic
    elif test_name == "Associate Archived API":
        # Expecting an error related to the archived API
        archived_api_id = edit_payload["apis"][0]["id"]
        expected_msg_dynamic = f"Cannot associate with archived API ID: {
            archived_api_id}"
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


def test_study_subject_get_all(get_admin, post_admin, create_study_subject):
    """
    Test retrieving all non-archived StudySubjects.
    """
    # Get existing StudySubjects length
    res = get_admin_study_subject(get_admin, study_subject_id=None)
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []
    existing_len = len(data_res)

    # Create multiple StudySubjects
    subject1 = create_study_subject(
        ditti_id="get_all_subject1_ditti_id",
        studies=[],
        apis=[]
    )
    subject2 = create_study_subject(
        ditti_id="get_all_subject2_ditti_id",
        studies=[],
        apis=[]
    )
    subject3 = create_study_subject(
        ditti_id="get_all_subject3_ditti_id",
        studies=[],
        apis=[]
    )

    # Archive one StudySubject
    subject3.is_archived = True
    db.session.commit()

    # Send GET request without 'id' to retrieve all StudySubjects
    res = get_admin_study_subject(get_admin, study_subject_id=None)

    # Check if response is empty
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    # Only two new non-archived subjects should be returned
    assert (len(data_res) - existing_len) == 2
    ditti_ids = [subject["dittiId"] for subject in data_res]
    assert "get_all_subject1_ditti_id" in ditti_ids
    assert "get_all_subject2_ditti_id" in ditti_ids
    assert "get_all_subject3_ditti_id" not in ditti_ids


def test_study_subject_get_by_id(get_admin, create_study_subject):
    """
    Test retrieving a specific StudySubject by ID.
    """
    # Create a StudySubject
    subject = create_study_subject(
        ditti_id="get_by_id_subject_ditti_id",
        studies=[],
        apis=[]
    )
    subject_id = subject.id

    # Send GET request with 'id' to retrieve the specific StudySubject
    res = get_admin_study_subject(get_admin, study_subject_id=subject_id)

    # Check if response is empty
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    assert len(data_res) == 1
    retrieved_subject = data_res[0]
    assert retrieved_subject["dittiId"] == "get_by_id_subject_ditti_id"
    assert retrieved_subject["id"] == subject_id


def test_study_subject_get_invalid_id_format(get_admin):
    """
    Test retrieving StudySubject with an invalid ID format.
    """
    # Send GET request with non-integer 'id'
    res = get_admin_study_subject(get_admin, study_subject_id="invalid_id")
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = {}

    # Assert response
    assert res.status_code == 400
    assert "msg" in data_res
    assert data_res["msg"] == "Invalid ID format. ID must be an integer."


def test_study_subject_get_non_existent_id(get_admin):
    """
    Test retrieving StudySubject with a non-existent ID.
    """
    # Assume ID 9999 does not exist
    res = get_admin_study_subject(get_admin, study_subject_id=9999)
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    assert len(data_res) == 0


def test_study_subject_get_archived_not_returned(get_admin, create_study_subject):
    """
    Test that archived StudySubjects are not returned in the list.
    """
    # Get existing StudySubjects length
    res = get_admin_study_subject(get_admin, study_subject_id=None)
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []
    existing_len = len(data_res)

    # Create StudySubjects
    subject1 = create_study_subject(
        ditti_id="archived_not_returned1_ditti_id",
        studies=[],
        apis=[]
    )
    subject2 = create_study_subject(
        ditti_id="archived_not_returned2_ditti_id",
        studies=[],
        apis=[]
    )

    # Archive one StudySubject
    subject2.is_archived = True
    db.session.commit()

    # Send GET request without 'id' to retrieve all StudySubjects
    res = get_admin_study_subject(get_admin, study_subject_id=None)
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    # Only one new non-archived subject should be returned
    assert (len(data_res) - existing_len) == 1
    assert data_res[-1]["dittiId"] == "archived_not_returned1_ditti_id"


def test_study_subject_get_archived_by_id(get_admin, create_study_subject):
    """
    Test retrieving an archived StudySubject by ID.
    """
    # Create and archive a StudySubject
    subject = create_study_subject(
        ditti_id="archived_by_id_ditti_id",
        studies=[],
        apis=[]
    )
    subject.is_archived = True
    db.session.commit()
    subject_id = subject.id

    # Send GET request with 'id' to retrieve the archived StudySubject
    res = get_admin_study_subject(get_admin, study_subject_id=subject_id)
    if res.data:
        data_res = json.loads(res.data)
    else:
        data_res = []

    # Assert response
    assert res.status_code == 200
    assert isinstance(data_res, list)
    assert len(data_res) == 0  # Archived subject should not be returned
