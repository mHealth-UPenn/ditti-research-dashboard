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

from install.utils.colorizer import Colorizer


def test_colorize_all_colors():
    """Test that colorize method works for all available colors."""
    text = "test text"
    for color in Colorizer.color_codes:
        if color == "reset":
            continue
        colored_text = Colorizer.colorize(text, color)
        assert colored_text.startswith(Colorizer.color_codes[color])
        assert colored_text.endswith(Colorizer.color_codes["reset"])
        assert text in colored_text


def test_individual_color_methods():
    """Test that individual color methods work correctly."""
    text = "test text"

    # Test each color method
    assert Colorizer.red(text).startswith(Colorizer.color_codes["red"])
    assert Colorizer.green(text).startswith(Colorizer.color_codes["green"])
    assert Colorizer.yellow(text).startswith(Colorizer.color_codes["yellow"])
    assert Colorizer.blue(text).startswith(Colorizer.color_codes["blue"])
    assert Colorizer.magenta(text).startswith(Colorizer.color_codes["magenta"])
    assert Colorizer.cyan(text).startswith(Colorizer.color_codes["cyan"])

    # Verify reset code is added
    for colored_text in [
        Colorizer.red(text),
        Colorizer.green(text),
        Colorizer.yellow(text),
        Colorizer.blue(text),
        Colorizer.magenta(text),
        Colorizer.cyan(text),
    ]:
        assert colored_text.endswith(Colorizer.color_codes["reset"])


def test_nested_colors():
    """Test that nested colors are handled correctly."""
    # Create text with nested colors
    inner_text = Colorizer.red("inner")
    outer_text = Colorizer.blue(f"outer {inner_text} outer")

    # Verify the structure
    assert outer_text.startswith(Colorizer.color_codes["blue"])
    assert "outer" in outer_text
    assert Colorizer.color_codes["red"] in outer_text
    assert "inner" in outer_text
    assert outer_text.endswith(Colorizer.color_codes["reset"])


def test_invalid_color():
    """Test that invalid colors raise an error."""
    with pytest.raises(KeyError):
        Colorizer.colorize("test", "invalid_color")  # type: ignore


def test_empty_text():
    """Test that empty text is handled correctly."""
    for color in Colorizer.color_codes:
        if color == "reset":
            continue
        colored_text = Colorizer.colorize("", color)
        assert colored_text.startswith(Colorizer.color_codes[color])
        assert colored_text.endswith(Colorizer.color_codes["reset"])
        assert len(colored_text) == len(Colorizer.color_codes[color]) + len(
            Colorizer.color_codes["reset"]
        )
