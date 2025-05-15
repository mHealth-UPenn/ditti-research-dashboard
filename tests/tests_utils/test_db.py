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
    study = Study.query.get(1)
    data = {"name": "baz", "acronym": "BAZ", "ditti_id": "BZ"}

    populate_model(study, data)
    db.session.commit()
    study = Study.query.get(1)
    assert study.name == "baz"
    assert study.acronym == "BAZ"
    assert study.ditti_id == "BZ"


def test_populate_model_invalid_attribute(app):
    study = Study.query.get(1)
    data = {"foo": "bar"}

    with pytest.raises(
        ValueError, match="Invalid attribute: foo \\(mapped to foo\\)"
    ):
        populate_model(study, data)


def test_populate_model_skip_lists(app):
    study = Study.query.get(1)
    data = {"name": ["baz"]}
    populate_model(study, data)
    db.session.commit()
    study = Study.query.get(1)
    assert study.name == "foo"


def test_populate_model_skip_joins(app):
    account = Account.query.get(2)
    study = Study.query.get(1)
    assert len(account.studies) == 1
    assert account.studies[0].study is study

    data = {"studies": "foo"}
    populate_model(account, data)
    db.session.commit()
    account = Account.query.get(2)
    assert len(account.studies) == 1
    assert account.studies[0].study is study


def test_populate_model_skip_relationships(app):
    access_group = AccessGroup.query.get(1)
    app = App.query.get(1)
    assert access_group.app == app

    data = {"app": "foo"}
    populate_model(access_group, data)
    db.session.commit()
    access_group = AccessGroup.query.get(1)
    assert access_group.app == app


def test_populate_model_camel_to_snake(app):
    study = Study.query.get(1)
    data = {
        "name": "baz",
        "acronym": "BAZ",
        "dittiId": "BZ",  # camelCase key
    }

    populate_model(study, data, use_camel_to_snake=True)
    db.session.commit()
    study = Study.query.get(1)
    assert study.name == "baz"
    assert study.acronym == "BAZ"
    assert study.ditti_id == "BZ"


def test_populate_model_custom_mapping(app):
    study = Study.query.get(1)
    data = {
        "studyName": "baz",  # Custom key
        "studyAcronym": "BAZ",
    }

    custom_mapping = {"studyName": "name", "studyAcronym": "acronym"}

    populate_model(study, data, custom_mapping=custom_mapping)
    db.session.commit()
    study = Study.query.get(1)

    # Updated assertions to reflect expected results
    assert study.name == "baz"
    assert study.acronym == "BAZ"
