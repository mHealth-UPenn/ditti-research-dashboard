# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from backend.extensions import db
from backend.models import AccessGroup, Account, App, Study
from backend.utils.db import populate_model


def test_populate_model(app):
    # Study model does not have 'version', testing with existing attrs
    data = {"name": "Test Study 2", "acronym": "TS2"}
    study = db.session.get(Study, 1)
    populate_model(study, data)
    db.session.commit()
    study = db.session.get(Study, 1)
    assert study.name == "Test Study 2"
    assert study.acronym == "TS2"
    # ensure original name is not overwritten if not in data


def test_populate_model_invalid_attribute(app):
    data = {"invalid_attribute": "Test Study 2"}
    study = db.session.get(Study, 1)
    # Check that populate_model raises ValueError for invalid attributes
    with pytest.raises(
        ValueError,
        match="Invalid attribute: invalid_attribute \\(mapped to invalid_attribute\\)",
    ):
        populate_model(study, data)
    db.session.commit()
    assert study.name == "foo"  # Name should remain unchanged


def test_populate_model_skip_lists(app):
    data = {"name": "Test Study 2", "roles": []}
    study = db.session.get(Study, 1)
    # roles should not be cleared
    populate_model(study, data)
    db.session.commit()
    study = db.session.get(Study, 1)
    assert study.name == "Test Study 2"
    assert len(study.roles) == 1


def test_populate_model_skip_joins(app):
    account = db.session.get(Account, 2)  # Account 2 is 'Jane Doe'
    data = {
        "email": "bar@test.com",
        "first_name": "Bar",
    }
    # ensure original values are not overwritten if not in data
    populate_model(account, data)
    db.session.commit()
    account = db.session.get(Account, 2)
    assert account.email == "bar@test.com"
    assert account.first_name == "Bar"
    assert account.last_name == "Smith"  # Original last_name is Smith


def test_populate_model_skip_relationships(app):
    data = {"name": "Test Access Group 2", "permissions": []}
    access_group = db.session.get(AccessGroup, 1)
    app = db.session.get(App, 1)
    # permissions should not be cleared
    populate_model(access_group, data)
    access_group.app = app
    db.session.commit()
    access_group = db.session.get(AccessGroup, 1)
    assert access_group.name == "Test Access Group 2"
    assert len(access_group.permissions) == 1


def test_populate_model_camel_to_snake(app):
    # Use 'consentInformation' which exists on the model
    data = {"name": "Test Study Camel", "consentInformation": "<p>Test</p>"}
    study = db.session.get(Study, 1)
    # Correct keyword arg: use_camel_to_snake
    populate_model(study, data, use_camel_to_snake=True)
    db.session.commit()
    study = db.session.get(Study, 1)
    assert study.name == "Test Study Camel"
    assert study.consent_information == "<p>Test</p>"
    # ensure original name is not overwritten if not in data


def test_populate_model_custom_mapping(app):
    # Use 'acronym' which exists on the model
    data = {"custom_name": "Test Study Custom", "custom_acronym": "TSC"}
    study = db.session.get(Study, 1)
    mapping = {"custom_name": "name", "custom_acronym": "acronym"}
    populate_model(study, data, custom_mapping=mapping)
    db.session.commit()
    study = db.session.get(Study, 1)
    assert study.name == "Test Study Custom"
    assert study.acronym == "TSC"
