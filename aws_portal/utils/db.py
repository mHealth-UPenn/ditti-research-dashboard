def populate_model(model, data):
    for k, v in data.items():
        if not hasattr(model, k):
            raise ValueError('Invalid attribute: %s' % k)

        if isinstance(v, list):
            continue

        setattr(model, k, v)
