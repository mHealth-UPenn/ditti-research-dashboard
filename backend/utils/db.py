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

from sqlalchemy.inspection import inspect

from backend.extensions import db
from backend.utils.serialization.serialization_common import camel_to_snake


def populate_model(model, data, use_camel_to_snake=False, custom_mapping=None):
    """
    Populate a SQLAlchemy model instance using a dictionary of data.

    Parameters
    ----------
        model (sqlalchemy.orm.Mapper): The SQLAlchemy model instance to populate.
        data (dict): A dictionary of key-value pairs.
        use_camel_to_snake (bool): If True, convert camelCase keys
            to snake_case before mapping.
        custom_mapping (dict): Optional custom mapping of camelCase keys
            to snake_case attributes.

    Raises
    ------
        ValueError: If an invalid key is encountered.
    """
    # Prepare a custom mapping or default to an empty dictionary
    custom_mapping = custom_mapping or {}

    # If camel_to_snake, retrieve all valid column attributes from the model
    model_columns = None
    if use_camel_to_snake:
        model_columns = {col.key for col in inspect(model).mapper.column_attrs}

    for k, v in data.items():
        original_key = k

        # Convert camelCase to snake_case and apply custom mapping if enabled
        if use_camel_to_snake or custom_mapping:
            k = custom_mapping.get(
                k, camel_to_snake(k) if use_camel_to_snake else k
            )

        # Check if the snake_case key is a valid model attribute
        if use_camel_to_snake and k not in model_columns:
            raise ValueError(f"Invalid attribute: {original_key} (mapped to {k})")

        # Ensure the attribute exists on the model
        try:
            attr = getattr(model, k)
        except AttributeError as err:
            raise ValueError(
                f"Invalid attribute: {original_key} (mapped to {k})"
            ) from err

        # Skip lists and relationships
        if isinstance(v, list):
            continue

        if isinstance(attr, list):
            continue

        if isinstance(attr, db.Model):
            continue

        # Set the attribute on the model
        setattr(model, k, v)
