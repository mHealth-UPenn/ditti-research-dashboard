import pytest
from install_scripts.utils.colorizer import Colorizer
from install_scripts.utils.types import Color


def test_colorize_all_colors():
    """Test that colorize method works for all available colors."""
    text = "test text"
    for color in Colorizer.color_codes.keys():
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
        Colorizer.cyan(text)
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
    for color in Colorizer.color_codes.keys():
        if color == "reset":
            continue
        colored_text = Colorizer.colorize("", color)
        assert colored_text.startswith(Colorizer.color_codes[color])
        assert colored_text.endswith(Colorizer.color_codes["reset"])
        assert len(colored_text) == len(Colorizer.color_codes[color]) + len(Colorizer.color_codes["reset"])
