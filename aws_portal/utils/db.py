from aws_portal.extensions import db


def populate_model(model, data):
    """
    Populate a model using a mapping class

    Args
    ----
    model: sqlalchemy.orm.Mapper
    data: dict
        a set of key, value pairs to population on the given model. Any keys
        that reference relationships are skipped

    Raises
    ------
    ValueError
        if a key is not an attriute of the mapper class
    """
    for k, v in data.items():
        if not hasattr(model, k):
            raise ValueError("Invalid attribute: %s" % k)

        if isinstance(v, list):
            continue

        if isinstance(getattr(model, k), list):
            continue

        if isinstance(getattr(model, k), db.Model):
            continue

        setattr(model, k, v)
