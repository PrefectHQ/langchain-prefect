import pytest
from prefect import Flow

from langchain.schema import (
    HumanMessage,
    SystemMessage,
)
from langchain_prefect import utilities as utils


@pytest.mark.parametrize(
    "text, expected_num_tokens",
    [
        ("", 0),
        (" ", 1),
        ("Hello, world!", 4),
        ("Foo bar baz", 3),
        ("Foo bar baz".split(), 3),
    ],
)
def test_num_tokens(text, expected_num_tokens):
    """Test that num_tokens returns the correct number of tokens."""
    assert utils.num_tokens(text) == expected_num_tokens


def test_flow_wrapped_fn():
    """Test that flow_wrapped_fn returns a flow."""

    def fn():
        pass

    async def async_fn():
        pass

    wrapped_sync_fn = utils.flow_wrapped_fn(fn)
    wrapped_async_fn = utils.flow_wrapped_fn(async_fn)

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
    assert utils.truncate(text, max_length) == expected_truncated_text


@pytest.mark.parametrize(
    "prompts, expected_prompt_content",
    [
        (
            [
                "You should speak like a pirate.",
                "I don't care about frogs.",
                "What did I just say?",
            ],
            [
                "You should speak like a pirate.",
                "I don't care about frogs.",
                "What did I just say?",
            ],
        ),
        (
            [
                SystemMessage(content="You should speak like a pirate."),
                HumanMessage(content="I don't care about frogs."),
                HumanMessage(content="What did I just say?"),
            ],
            [
                "You should speak like a pirate.",
                "I don't care about frogs.",
                "What did I just say?",
            ],
        ),
        (
            [
                [
                    SystemMessage(content="You should speak like a pirate."),
                    HumanMessage(content="I don't care about frogs."),
                    HumanMessage(content="What did I just say?"),
                ]
            ],
            [
                "You should speak like a pirate.",
                "I don't care about frogs.",
                "What did I just say?",
            ],
        ),
    ],
)
def test_get_prompt_content(prompts, expected_prompt_content):
    """Test that get_prompt_content returns the correct content."""
    assert utils.get_prompt_content(prompts) == expected_prompt_content
