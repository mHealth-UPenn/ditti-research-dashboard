import re

from pydantic import ConfigDict


def snake_to_camel(string: str) -> str:
    """Convert a snake_case string to camelCase."""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def camel_to_snake(name: str) -> str:
    """Convert a camelCase string to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


common_config = ConfigDict(
    from_attributes=True,
    extra="forbid",  # Disallow extra fields
    alias_generator=snake_to_camel,
    populate_by_name=True,
    use_enum_values=True,
)
