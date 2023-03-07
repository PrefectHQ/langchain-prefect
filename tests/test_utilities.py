import pytest

from prefect_langchain.utilities import num_tokens


@pytest.mark.parametrize(
    "text, expected_num_tokens",
    [
        ("", 0),
        (" ", 1),
        ("Hello, world!", 4),
        ("Foo bar baz", 5),
        ("Foo bar baz".split(), 5),
    ],
)
def test_num_tokens(text, expected_num_tokens):
    """Test that num_tokens returns the correct number of tokens."""
    assert num_tokens(text) == expected_num_tokens
