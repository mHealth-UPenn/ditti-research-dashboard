from aws_portal.extensions import db


def populate_model(model, data):
    for k, v in data.items():
        if not hasattr(model, k):
            raise ValueError('Invalid attribute: %s' % k)

        if isinstance(v, list):
            continue

        if isinstance(getattr(model, k), list):
            continue

        if isinstance(getattr(model, k), db.Model):
            continue

        setattr(model, k, v)
