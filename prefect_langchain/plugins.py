"""Module for defining Prefect plugins for langchain."""
from contextlib import ContextDecorator
from functools import wraps
from typing import Any, Callable

import pendulum
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult
from prefect import Flow, flow
from prefect import tags as prefect_tags
from prefect.utilities.asyncutils import is_async_fn
from pydantic import BaseModel

from prefect_langchain.utilities import num_tokens


class NotAnArtifact(BaseModel):
    """Placeholder class for soon-to-come `Artifact`."""

    name: str
    description: str
    content: Any


def llm_invocation_summary(*args, **kwargs) -> NotAnArtifact:
    """Will eventually return an artifact."""

    llm_endpoint = args[0].__module__
    text_input = str(args[-1])

    return NotAnArtifact(
        name="LLM Invocation Summary",
        description=f"Query {llm_endpoint}",
        content={"llm_endpoint": llm_endpoint, "text_input": text_input, **kwargs},
    )


def parse_llm_result(llm_result: LLMResult) -> NotAnArtifact:
    """Will eventually return an artifact."""
    return NotAnArtifact(
        name="LLM Result",
        description="The result of the LLM invocation.",
        content=llm_result,
    )


def flow_wrapped_fn(
    func: Callable[..., LLMResult],
    flow_kwargs,
    *args,
    **kwargs,
) -> Flow:
    """Define a function to be wrapped in a flow depending
    on whether the original function is sync or async."""
    if is_async_fn(func):

        async def execute_async_llm_call(text_input: str, llm_endpoint: str):
            """async flow for async LLM calls via `SubclassofBaseLLM.agenerate`"""
            print(f"Sending {text_input} to {llm_endpoint}")
            llm_result: LLMResult = await func(*args, **kwargs)
            print(f"Recieved: {parse_llm_result(llm_result)}")
            return llm_result

        return flow(**flow_kwargs)(execute_async_llm_call)
    else:

        def execute_llm_call(text_input: str, llm_endpoint: str):
            """sync flow for sync LLM calls via `SubclassofBaseLLM.generate`"""
            print(f"Sending {text_input} to {llm_endpoint}")
            llm_result: LLMResult = func(*args, **kwargs)
            print(f"Recieved: {parse_llm_result(llm_result)}")
            return llm_result

        return flow(**flow_kwargs)(execute_llm_call)


def record_llm_call(
    func: Callable[..., LLMResult],
    tags: set | None = None,
    flow_kwargs: dict | None = None,
    max_prompt_tokens: int = int(1e3),
) -> Callable[..., Flow]:
    """Decorator for wrapping a Langchain LLM call with a prefect flow."""

    tags = tags or set()
    flow_kwargs = flow_kwargs or dict(name="Execute LLM Call", log_prints=True)

    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper for LLM calls"""
        invocation_artifact = llm_invocation_summary(
            invocation_fn=func, *args, **kwargs
        )

        llm_endpoint = invocation_artifact.content["llm_endpoint"]
        text_input = invocation_artifact.content["text_input"]

        if num_tokens(text_input) > max_prompt_tokens:
            raise ValueError(
                f"Prompt is too long - it contains {num_tokens(text_input)} tokens"
                f" and {max_prompt_tokens=}. Did not call {llm_endpoint}."
            )

        llm_generate = flow_wrapped_fn(func, flow_kwargs, *args, **kwargs)

        with prefect_tags(*[llm_endpoint, *tags]):
            return llm_generate.with_options(
                flow_run_name=f"Calling {llm_endpoint} at {pendulum.now().strftime('%Y-%m-%d %H:%M:%S')}"  # noqa: E501
            )(
                text_input=text_input,
                llm_endpoint=llm_endpoint,
            )

    return wrapper


class RecordLLMCalls(ContextDecorator):
    """Context manager for patching LLM calls with a prefect flow."""

    def __init__(self, **decorator_kwargs):
        """Constructor for `RecordLLMCalls`. Accepts `tags`, `flow_kwargs`, and `max_prompt_tokens`.

        Example:
            Create a flow with `a_custom_tag` upon calling `OpenAI.generate`:

            >>> with RecordLLMCalls(tags={"a_custom_tag"}):
            >>>    llm = OpenAI(temperature=0.9)
            >>>    llm(
            >>>        "What would be a good company name "
            >>>        "for a company that makes carbonated water?"
            >>>    )

            Create an async flow upon calling `OpenAI.agenerate`:

            >>> with RecordLLMCalls():
            >>>    llm = OpenAI(temperature=0.9)
            >>>    await llm.agenerate(
            >>>        [
            >>>            "What would be a good name for a company that makes colorful socks?",
            >>>            "What would be a good name for a company that sells carbonated water?",
            >>>        ]
            >>>    )

            Create a flow for LLM calls and enforce a max number of tokens in the prompt: # noqa: E501

            >>> with RecordLLMCalls(max_prompt_tokens=100):
            >>>    llm = OpenAI(temperature=0.9)
            >>>    llm(
            >>>        "What would be a good company name "
            >>>        "for a company that makes carbonated water?"
            >>>    )
        """
        self.decorator_kwargs = decorator_kwargs

    def __enter__(self):
        """Called when entering the context manager."""
        self.patched_methods = []
        for cls in BaseLLM.__subclasses__():
            self._patch_method(cls, "agenerate", record_llm_call)
            self._patch_method(cls, "generate", record_llm_call)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the context manager."""
        for cls, method_name, original_method in self.patched_methods:
            setattr(cls, method_name, original_method)

    def _patch_method(self, cls, method_name, decorator):
        """Patch a method on a class with a decorator."""
        original_method = getattr(cls, method_name)
        modified_method = decorator(original_method, **self.decorator_kwargs)
        setattr(cls, method_name, modified_method)
        self.patched_methods.append((cls, method_name, original_method))
