import pytest
from aws_portal.extensions import db
from aws_portal.models import AccessGroup, Account, App, Study
from aws_portal.utils.db import populate_model


def test_populate_model(app):
    study = Study.query.get(1)
    data = {
        'name': 'baz',
        'acronym': 'BAZ',
        'ditti_id': 'BZ'
    }

    populate_model(study, data)
    db.session.commit()
    study = Study.query.get(1)
    assert study.name == 'baz'
    assert study.acronym == 'BAZ'
    assert study.ditti_id == 'BZ'


def test_populate_model_invalid_attribute(app):
    study = Study.query.get(1)
    data = {'foo': 'bar'}

    with pytest.raises(ValueError) as e:
        populate_model(study, data)

    assert str(e.value) == 'Invalid attribute: foo'


def test_populate_model_skip_lists(app):
    study = Study.query.get(1)
    data = {'name': ['baz']}
    populate_model(study, data)
    db.session.commit()
    study = Study.query.get(1)
    assert study.name == 'foo'


def test_populate_model_skip_joins(app):
    account = Account.query.get(2)
    study = Study.query.get(1)
    assert len(account.studies) == 1
    assert account.studies[0].study is study

    data = {'studies': 'foo'}
    populate_model(account, data)
    db.session.commit()
    account = Account.query.get(2)
    assert len(account.studies) == 1
    assert account.studies[0].study is study


def test_populate_model_skip_relationships(app):
    access_group = AccessGroup.query.get(1)
    app = App.query.get(1)
    assert access_group.app == app

    data = {'app': 'foo'}
    populate_model(access_group, data)
    db.session.commit()
    access_group = AccessGroup.query.get(1)
    assert access_group.app == app
