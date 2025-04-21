# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sqlalchemy.inspection import inspect

from backend.extensions import db
from backend.utils.serialization.serialization_common import camel_to_snake


def populate_model(model, data, use_camel_to_snake=False, custom_mapping=None):
    """
    Populate a SQLAlchemy model instance using a dictionary of data.

    Args:
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
        except AttributeError:
            raise ValueError(f"Invalid attribute: {original_key} (mapped to {k})")

        # Skip lists and relationships
        if isinstance(v, list):
            continue

        if isinstance(attr, list):
            continue

        if isinstance(attr, db.Model):
            continue

        # Set the attribute on the model
        setattr(model, k, v)
