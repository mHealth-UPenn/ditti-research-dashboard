from sqlalchemy.inspection import inspect
from aws_portal.extensions import db
from aws_portal.utils.serialization.serialization_common import camel_to_snake


def populate_model(model, data, use_camel_to_snake=False, custom_mapping=None):
    """
    Populate a SQLAlchemy model instance using a dictionary of data.

    Args:
        model (sqlalchemy.orm.Mapper): The SQLAlchemy model instance to populate.
        data (dict): A dictionary of key-value pairs.
        use_camel_to_snake (bool): If True, convert camelCase keys to snake_case before mapping.
        custom_mapping (dict): Optional custom mapping of camelCase keys to snake_case attributes.

    Raises:
        ValueError: If an invalid key is encountered.
    """
    # Prepare a custom mapping or default to an empty dictionary
    custom_mapping = custom_mapping or {}

    # Retrieve all valid column attributes from the model if camel_to_snake is used
    model_columns = None
    if use_camel_to_snake:
        model_columns = {col.key for col in inspect(model).mapper.column_attrs}

    for k, v in data.items():
        original_key = k

        # Convert camelCase to snake_case and apply custom mapping if enabled
        if use_camel_to_snake or custom_mapping:
            k = custom_mapping.get(k, camel_to_snake(
                k) if use_camel_to_snake else k)

        # Check if the snake_case key is a valid model attribute
        if use_camel_to_snake and k not in model_columns:
            raise ValueError(f"Invalid attribute: {original_key} "
                             f"(mapped to {k})")

        # Ensure the attribute exists on the model
        try:
            attr = getattr(model, k)
        except AttributeError:
            raise ValueError(f"Invalid attribute: {original_key} "
                             f"(mapped to {k})")

        # Skip lists and relationships
        if isinstance(v, list):
            continue

        if isinstance(attr, list):
            continue

        if isinstance(attr, db.Model):
            continue

        # Set the attribute on the model
        setattr(model, k, v)
