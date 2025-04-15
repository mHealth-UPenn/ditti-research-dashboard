import re

from install_scripts.utils.types import Env


def is_valid_name(name: str) -> bool:
    """Validate project name."""
    if not name:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name)) and len(name) <= 64


def is_valid_email(email: str) -> bool:
    """Validate email address."""
    if not email:
        return False
    return bool(
        re.match(r"^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", email)
    )


def get_project_suffix(env: Env) -> str:
    match env:
        case "dev":
            return "dev"
        case "staging":
            return "staging"
        case _:
            return ""
