from pydantic import ConfigDict


def to_camel(string: str) -> str:
    """
    Converts a snake_case string to camelCase.
    """
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


common_config = ConfigDict(
    from_attributes=True,
    extra="forbid",  # Disallow extra fields
    alias_generator=to_camel,
    populate_by_name=True,
    use_enum_values=True,
    exclude_none=True
)
