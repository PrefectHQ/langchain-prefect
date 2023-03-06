"""Utilities for the prefect_langchain package."""

import tiktoken


def num_tokens(text: str) -> int:
    """Return the number of tokens in the text."""
    return len(tiktoken.encoding_for_model("text-davinci-003").encode(text))
