from datetime import datetime, timedelta, UTC
import os
from unittest.mock import patch, Mock
from backend.extensions import db
from backend.models import (
    AccessGroup, Account, App, BlockedToken, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinAccountStudy, JoinRolePermission,
    JoinStudyRole, Permission, Role, Study, StudySubject, JoinStudySubjectApi,
    JoinStudySubjectStudy, Api
)

# Validate the SQLAlchemy URI
uri = os.getenv("FLASK_DB")
if "localhost" not in uri:
    raise Exception(
        "The SQLAlchemy URI does not point to localhost. Run `source deploy-" +
        "dev.sh` before running pytest. Current URI:",
        uri
    )

# Test data for various models
apps = [
    {
        "name": "foo"
    },
    {
        "name": "bar"
    }
]

access_groups = [
    {
        "name": "foo"
    },
    {
        "name": "bar"
    }
]

accounts = [
    {
        "created_on": datetime.now(UTC),
        "first_name": "John",
        "last_name": "Smith",
        "email": "foo@email.com",
        "is_confirmed": True
    },
    {
        "created_on": datetime.now(UTC),
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "bar@email.com"
    }
]

permissions = [
    {
        "action": "foo",
        "resource": "baz"
    },
    {
        "action": "bar",
        "resource": "baz"
    },
    {
        "action": "bar",
        "resource": "qux"
    },
    {
        "action": "Edit",
        "resource": "User"
    },
    {
        "action": "Create",
        "resource": "User"
    }
]

roles = [
    {
        "name": "foo"
    },
    {
        "name": "bar"
    }
]

studies = [
    {
        "name": "foo",
        "acronym": "FOO",
        "ditti_id": "FO",
        "email": "foo@study.com",
        "is_archived": False,
        "default_expiry_delta": 14,
        "consent_information": "foo",
        "data_summary": None,
        "is_qi": False
    },
    {
        "name": "bar",
        "acronym": "BAR",
        "ditti_id": "BR",
        "email": "bar@study.com",
        "is_archived": False,
        "default_expiry_delta": 14,
        "consent_information": "foo",
        "data_summary": None,
        "is_qi": False
    }
]

blocked_tokens = [
    {
        "jti": "foo",
        "created_on": datetime.now(UTC)
    },
    {
        "jti": "bar",
        "created_on": datetime.now(UTC)
    }
]

study_subjects = [
    {
        "created_on": datetime.now(UTC),
        "ditti_id": "ditti_foo_123",
    },
    {
        "created_on": datetime.now(UTC),
        "ditti_id": "ditti_bar_456",
    }
]

apis = [
    {
        "name": "foo",
    },
    {
        "name": "bar",
    }
]


def create_tables():
    # Add Apps
    for app_data in apps:
        db.session.add(App(**app_data))

    # Add AccessGroups
    for access_group_data in access_groups:
        db.session.add(AccessGroup(**access_group_data))

    # Add Accounts
    for account_data in accounts:
        db.session.add(Account(**account_data))

    # Add Permissions
    for permission_data in permissions:
        p = Permission()
        p.action = permission_data["action"]
        p.resource = permission_data["resource"]
        db.session.add(p)

    # Add Roles
    for role_data in roles:
        db.session.add(Role(**role_data))

    # Add Studies with all required fields
    for study_data in studies:
        db.session.add(Study(**study_data))

    # Add BlockedTokens
    for blocked_token_data in blocked_tokens:
        db.session.add(BlockedToken(**blocked_token_data))

    # Add StudySubjects with ditti_id
    for study_subject_data in study_subjects:
        db.session.add(StudySubject(**study_subject_data))

    # Add APIs
    for api_data in apis:
        db.session.add(Api(**api_data))


def create_joins():
    # Associate AccessGroups with Apps
    foo_access_group = AccessGroup.query.filter(
        AccessGroup.name == "foo").first()
    foo_app = App.query.filter(App.name == "foo").first()
    foo_access_group.app = foo_app

    bar_access_group = AccessGroup.query.filter(
        AccessGroup.name == "bar").first()
    bar_app = App.query.filter(App.name == "bar").first()
    bar_access_group.app = bar_app

    # Associate AccessGroups with Permissions
    foo_permission = Permission.query.filter(
        Permission.action == "foo", Permission.resource == "baz"
    ).first()
    foo_join = JoinAccessGroupPermission(
        access_group=foo_access_group,
        permission=foo_permission
    )
    db.session.add(foo_join)

    bar_permission = Permission.query.filter(
        Permission.action == "bar", Permission.resource == "baz"
    ).first()
    bar_join = JoinAccessGroupPermission(
        access_group=bar_access_group,
        permission=bar_permission
    )
    db.session.add(bar_join)

    # Associate Roles with Permissions
    role_foo = Role.query.filter(Role.name == "foo").first()
    perm_foo_baz = Permission.query.filter(
        Permission.action == "foo", Permission.resource == "baz"
    ).first()
    perm_edit_user = Permission.query.filter(
        Permission.action == "Edit", Permission.resource == "User"
    ).first()
    perm_create_user = Permission.query.filter(
        Permission.action == "Create", Permission.resource == "User"
    ).first()

    join_role_perm_foo_baz = JoinRolePermission(
        role=role_foo,
        permission=perm_foo_baz
    )
    join_role_perm_edit_user = JoinRolePermission(
        role=role_foo,
        permission=perm_edit_user
    )
    join_role_perm_create_user = JoinRolePermission(
        role=role_foo,
        permission=perm_create_user
    )
    db.session.add(join_role_perm_foo_baz)
    db.session.add(join_role_perm_edit_user)
    db.session.add(join_role_perm_create_user)

    perm_bar_qux = Permission.query.filter(
        Permission.action == "bar", Permission.resource == "qux"
    ).first()
    role_bar = Role.query.filter(Role.name == "bar").first()
    join_role_perm_bar_qux = JoinRolePermission(
        role=role_bar,
        permission=perm_bar_qux
    )
    db.session.add(join_role_perm_bar_qux)

    # Associate Roles with Studies
    study_foo = Study.query.filter(Study.name == "foo").first()
    join_study_role_foo = JoinStudyRole(
        role=role_foo,
        study=study_foo
    )
    db.session.add(join_study_role_foo)

    study_bar = Study.query.filter(Study.name == "bar").first()
    join_study_role_bar = JoinStudyRole(
        role=role_bar,
        study=study_bar
    )
    db.session.add(join_study_role_bar)

    # Associate Accounts with AccessGroups
    account_foo = Account.query.filter(
        Account.email == "foo@email.com").first()
    account_bar = Account.query.filter(
        Account.email == "bar@email.com").first()

    join_account_access_group_foo = JoinAccountAccessGroup(
        account=account_foo,
        access_group=foo_access_group
    )
    join_account_access_group_bar = JoinAccountAccessGroup(
        account=account_bar,
        access_group=bar_access_group
    )
    db.session.add(join_account_access_group_foo)
    db.session.add(join_account_access_group_bar)

    # Associate Accounts with Studies and Roles
    join_account_study_foo = JoinAccountStudy(
        account=account_foo,
        study=study_foo,
        role=role_foo
    )
    join_account_study_bar = JoinAccountStudy(
        account=account_bar,
        study=study_bar,
        role=role_bar
    )
    db.session.add(join_account_study_foo)
    db.session.add(join_account_study_bar)

    # Associate StudySubjects with Studies
    study_subject_foo = StudySubject.query.filter(
        StudySubject.ditti_id == "ditti_foo_123"
    ).first()
    study_subject_bar = StudySubject.query.filter(
        StudySubject.ditti_id == "ditti_bar_456"
    ).first()

    join_study_subject_study_foo = JoinStudySubjectStudy(
        study_subject=study_subject_foo,
        study=study_foo,
        expires_on=datetime.now(UTC) + timedelta(days=14),
    )
    join_study_subject_study_bar = JoinStudySubjectStudy(
        study_subject=study_subject_bar,
        study=study_bar,
        expires_on=datetime.now(UTC) + timedelta(days=14),
    )
    db.session.add(join_study_subject_study_foo)
    db.session.add(join_study_subject_study_bar)

    # Associate StudySubjects with APIs
    api_foo = Api.query.filter(Api.name == "foo").first()
    api_bar = Api.query.filter(Api.name == "bar").first()

    join_study_subject_api_foo = JoinStudySubjectApi(
        study_subject=study_subject_foo,
        api=api_foo,
        api_user_uuid="foo",
        scope=["foo", "bar"]
    )
    join_study_subject_api_bar = JoinStudySubjectApi(
        study_subject=study_subject_bar,
        api=api_bar,
        api_user_uuid="bar",
        scope=["foo", "bar"]
    )
    db.session.add(join_study_subject_api_foo)
    db.session.add(join_study_subject_api_bar)


# New helper functions for Cognito authentication
def mock_cognito_tokens():
    """Generate mock Cognito tokens for testing."""
    return {
        "access_token": "mock_access_token",
        "id_token": "mock_id_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600
    }


def setup_auth_flow_session(client, user_type="participant"):
    """Set up a mock authentication flow session."""
    # Use the simpler session approach that was working in the test files
    with client.session_transaction() as flask_session:
        flask_session["cognito_state"] = "mock_state"
        flask_session["cognito_code_verifier"] = "mock_code_verifier"
        flask_session["cognito_nonce"] = "mock_nonce"
        flask_session["cognito_nonce_generated"] = int(
            datetime.now().timestamp())
        flask_session["auth_flow_user_type"] = user_type

    return "mock_state"


def get_unwrapped_view(view_module, view_func_name):
    """
    Unwrap a view function to access the underlying implementation.

    This allows testing the core view logic without authentication
    decorators getting in the way.
    """
    import inspect
    from functools import wraps

    # Get the wrapped view function
    view_func = getattr(view_module, view_func_name)

    # Recursively unwrap until we get the core function
    while hasattr(view_func, "__wrapped__"):
        view_func = view_func.__wrapped__

    return view_func


def mock_researcher_auth_for_testing(client, is_admin=True):
    """
    Mock researcher authentication for testing admin views.

    Instead of going through the login flow, this directly simulates
    an authenticated researcher (admin or non-admin).

    Args:
        client: Flask test client
        is_admin: Whether to make the mocked researcher an admin

    Returns:
        Headers dict with authentication token
    """
    # Create a mock account for the researcher
    from backend.models import Account
    mock_account = Account.query.filter_by(email="foo@email.com").first()

    # Generate a mock ID token
    mock_token = "mock_id_token_for_researcher"

    # Create headers with the mock token
    headers = {
        "Authorization": f"Bearer {mock_token}"
    }

    # Patch the ResearcherAuthController to return our mock account
    from unittest.mock import patch, MagicMock
    from backend.auth.controllers.researcher import ResearcherAuthController

    # Apply the patch to the client's application context
    patcher1 = patch.object(
        ResearcherAuthController,
        'get_user_from_token',
        return_value=(mock_account, None)
    )
    patcher1.start()

    # Also patch the check_permissions function to always return True
    from backend.auth.decorators.researcher import check_permissions
    patcher2 = patch(
        'backend.auth.decorators.researcher.check_permissions',
        return_value=(True, None)
    )
    patcher2.start()

    patchers = [patcher1, patcher2]

    # Patch any Cognito-related functions with the correct method names
    # For account creation in Cognito
    try:
        patcher3 = patch.object(
            ResearcherAuthController,
            'create_account_in_cognito',
            return_value=(True, None)
        )
        patcher3.start()
        patchers.append(patcher3)

        # For updating user attributes in Cognito
        patcher4 = patch.object(
            ResearcherAuthController,
            'update_account_in_cognito',
            return_value=(True, None)
        )
        patcher4.start()
        patchers.append(patcher4)

        # For deleting/disabling users in Cognito
        patcher5 = patch.object(
            ResearcherAuthController,
            'disable_account_in_cognito',
            return_value=(True, None)
        )
        patcher5.start()
        patchers.append(patcher5)

    except (ImportError, AttributeError) as e:
        # If these modules or methods don't exist, just continue
        print(f"Skipping some patchers due to: {e}")
        pass

    # Store the patchers in the client for cleanup
    if not hasattr(client, '_auth_patchers'):
        client._auth_patchers = []
    client._auth_patchers.extend(patchers)

    return headers


# Additional testing utilities for mock standardization

def mock_db_query_result(model_class, result_or_results):
    """
    Mock a database query to return specific results.

    This is a more flexible alternative to mock_model_not_found that allows
    specifying the exact return values.

    Args:
        model_class: The SQLAlchemy model class to mock
        result_or_results: Single object or list of objects to return from the query

    Returns:
        Mock query object

    Example:
        # Mock User.query to return a specific user
        user = User(id=1, name="Test User")
        mock_db_query_result(User, user)

        # Mock User.query to return multiple users
        users = [User(id=1), User(id=2)]
        mock_db_query_result(User, users)
    """
    from unittest.mock import patch, MagicMock

    patcher = patch.object(model_class, 'query')
    mock_query = patcher.start()

    # Create mock filter methods
    mock_filter = MagicMock()

    # Configure return values based on input type
    if isinstance(result_or_results, list):
        mock_filter.all.return_value = result_or_results
        mock_filter.first.return_value = result_or_results[0] if result_or_results else None
    else:
        mock_filter.all.return_value = [
            result_or_results] if result_or_results else []
        mock_filter.first.return_value = result_or_results

    # Setup common query methods
    mock_query.filter_by.return_value = mock_filter
    mock_query.filter.return_value = mock_filter
    mock_query.get.side_effect = lambda id: result_or_results if result_or_results and getattr(
        result_or_results, 'id', None) == id else None

    return mock_query


def mock_boto3_client(service_name, mock_methods=None):
    """
    Create a standardized mock for boto3 clients.

    Args:
        service_name: Name of the AWS service (e.g., 'cognito-idp')
        mock_methods: Dict of method names and their return values or side effects

    Returns:
        Mock boto3 client

    Example:
        # Mock Cognito client with specific method responses
        mock_boto3_client('cognito-idp', {
            'admin_get_user': {'User': {'Username': 'test-user'}},
            'admin_delete_user': None,  # Returns None
            'admin_create_user': Exception("User already exists")  # Raises exception
        })
    """
    from unittest.mock import patch, MagicMock

    mock_client = MagicMock()

    # Configure methods if provided
    if mock_methods:
        for method_name, return_value in mock_methods.items():
            method_mock = getattr(mock_client, method_name)
            if isinstance(return_value, Exception):
                method_mock.side_effect = return_value
            else:
                method_mock.return_value = return_value

    # Patch boto3.client to return our mock
    patcher = patch('boto3.client', return_value=mock_client)
    mock_boto3 = patcher.start()

    return mock_client
