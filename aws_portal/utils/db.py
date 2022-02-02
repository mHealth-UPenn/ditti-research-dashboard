def populate_model(model, data):
    for k, v in data.items():
        if hasattr(model, k):
            setattr(model, k, v)

        else:
            raise ValueError('Invalid attribute: %s' % k)
