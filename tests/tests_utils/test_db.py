import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import Study, init_db
from aws_portal.utils.db import populate_model
from tests.testing_utils import create_joins, create_tables


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        create_tables()
        create_joins()
        db.session.commit()
        yield app


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
