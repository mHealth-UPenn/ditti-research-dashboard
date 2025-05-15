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

import pytest

from install.utils.utils import is_valid_email, is_valid_name


@pytest.mark.parametrize(
    "name",
    [
        "my-project",
        "my_project",
        "project123",
        "a" * 64,
    ],
)
def test_valid_names(name):
    """Test various valid project names."""
    assert is_valid_name(name) is True


@pytest.mark.parametrize(
    "name",
    [
        "",
        None,
        "my/project",
        "my.project",
        "my project",
        "my@project",
        "a" * 65,
        "My Project!",
        "Project-123",
    ],
)
def test_invalid_names(name):
    """Test various invalid project names."""
    assert is_valid_name(name) is False


@pytest.mark.parametrize(
    "email",
    [
        "user@example.com",
        "user.name@example.com",
        "user+label@example.com",
        "user@subdomain.example.com",
        "user@example.co.uk",
        "user123@example.com",
        "user@example.org",
    ],
)
def test_valid_emails(email):
    """Test various valid email addresses."""
    assert is_valid_email(email) is True


@pytest.mark.parametrize(
    "email",
    [
        "",
        None,
        "user@",
        "@example.com",
        "user@example",
        "user@.com",
        "user@example.",
        "user@example..com",
        "user@example@example.com",
        "user@example.com.",
        "user@example.c",
    ],
)
def test_invalid_emails(email):
    """Test various invalid email addresses."""
    assert is_valid_email(email) is False
