"""Module for defining Prefect plugins for langchain."""

from contextlib import ContextDecorator
from functools import wraps
from typing import Callable

from langchain.schema import LLMResult
from langchain.base_language import BaseLanguageModel
from prefect import Flow
from prefect import tags as prefect_tags

from langchain_prefect.utilities import (
    flow_wrapped_fn,
    get_prompt_content,
    llm_invocation_summary,
    num_tokens,
)


def record_llm_call(
    func: Callable[..., LLMResult],
    tags: set | None = None,
    max_prompt_tokens: int | None = int(1e4),
    flow_kwargs: dict | None = None,
) -> Callable[..., Flow]:
    """Decorator for wrapping a Langchain LLM call with a prefect flow."""

    tags = tags or set()

    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper for LLM calls"""
        invocation_artifact = llm_invocation_summary(
            invocation_fn=func, *args, **kwargs
        )

        llm_endpoint = invocation_artifact.content["llm_endpoint"]
        prompts = invocation_artifact.content["prompts"]

        if max_prompt_tokens and (
            (N := num_tokens(get_prompt_content(prompts))) > max_prompt_tokens
        ):
            raise ValueError(
                f"Prompt is too long: it contains {N} tokens"
                f" and {max_prompt_tokens=}. Did not call {llm_endpoint!r}. "
                "If desired, increase `max_prompt_tokens`."
            )

        llm_generate = flow_wrapped_fn(func, flow_kwargs, *args, **kwargs)

        with prefect_tags(*[llm_endpoint, *tags]):
            return llm_generate.with_options(
                flow_run_name=f"Calling {llm_endpoint}"  # noqa: E501
            )(llm_input=invocation_artifact)

    return wrapper


class RecordLLMCalls(ContextDecorator):
    """Context decorator for patching LLM calls with a prefect flow."""

    def __init__(self, **decorator_kwargs):
        """Context decorator for patching LLM calls with a prefect flow.

        Args:
            tags: Tags to apply to flow runs created by this context manager.
            flow_kwargs: Keyword arguments to pass to the flow decorator.
            max_prompt_tokens: The maximum number of tokens allowed in a prompt.

        Example:
            Create a flow with `a_custom_tag` upon calling `OpenAI.generate`:

            >>> with RecordLLMCalls(tags={"a_custom_tag"}):
            >>>    llm = OpenAI(temperature=0.9)
            >>>    llm(
            >>>        "What would be a good company name "
            >>>        "for a company that makes carbonated water?"
            >>>    )

            Track many LLM calls when using a langchain agent

            >>> llm = OpenAI(temperature=0)
            >>> tools = load_tools(["llm-math"], llm=llm)
            >>> agent = initialize_agent(tools, llm)

            >>> @flow
            >>> def my_flow():  # noqa: D103
            >>>     agent.run(
            >>>         "How old is the current Dalai Lama? "
            >>>         "What is his age divided by 2 (rounded to the nearest integer)?"
            >>>     )

            >>> with RecordLLMCalls():
            >>>     my_flow()

            Create an async flow upon calling `OpenAI.agenerate`:

            >>> with RecordLLMCalls():
            >>>    llm = OpenAI(temperature=0.9)
            >>>    await llm.agenerate(
            >>>        [
            >>>            "Good name for a company that makes colorful socks?",
            >>>            "Good name for a company that sells carbonated water?",
            >>>        ]
            >>>    )

            Create flow for LLM call and enforce a max number of tokens in the prompt:

            >>> with RecordLLMCalls(max_prompt_tokens=100):
            >>>    llm = OpenAI(temperature=0.9)
            >>>    llm(
            >>>        "What would be a good company name "
            >>>        "for a company that makes carbonated water?"
            >>>    )
        """
        self.decorator_kwargs = decorator_kwargs

    def __enter__(self):
        """Called when entering the context manager.

        This is what would need to be changed if Langchain started making
        LLM api calls in a different place.
        """
        self.patched_methods = []
        for subcls in BaseLanguageModel.__subclasses__():
            if subcls.__name__ == "BaseChatModel":
                for subsubcls in subcls.__subclasses__():
                    # patch `BaseChatModel` generate methods when used as callable
                    self._patch_method(subsubcls, "_generate", record_llm_call)
                    self._patch_method(subsubcls, "_agenerate", record_llm_call)

            self._patch_method(subcls, "generate", record_llm_call)
            self._patch_method(subcls, "agenerate", record_llm_call)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset methods when exiting the context manager."""
        for cls, method_name, original_method in self.patched_methods:
            setattr(cls, method_name, original_method)

    def _patch_method(self, cls, method_name, decorator):
        """Patch a method on a class with a decorator."""
        original_method = getattr(cls, method_name)
        modified_method = decorator(original_method, **self.decorator_kwargs)
        setattr(cls, method_name, modified_method)
        self.patched_methods.append((cls, method_name, original_method))
