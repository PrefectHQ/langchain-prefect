import pytest
from prefect import Flow

from langchain_prefect.utilities import flow_wrapped_fn, num_tokens, truncate


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


def test_flow_wrapped_fn():
    """Test that flow_wrapped_fn returns a flow."""

    def fn():
        pass

    async def async_fn():
        pass

    wrapped_sync_fn = flow_wrapped_fn(fn)
    wrapped_async_fn = flow_wrapped_fn(async_fn)

    assert isinstance(wrapped_sync_fn, Flow)
    assert isinstance(wrapped_async_fn, Flow)


@pytest.mark.parametrize(
    "text, max_length, expected_truncated_text",
    [
        ("123", 4, "123"),
        ("123", 3, "123"),
        ("ICE ICE BABY", 10, "ICE...ABY"),
    ],
)
def test_truncate(text, max_length, expected_truncated_text):
    """Test that truncate returns the correct truncated text."""
    assert truncate(text, max_length) == expected_truncated_text
