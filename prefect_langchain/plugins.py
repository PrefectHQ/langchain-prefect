"""Module for defining Prefect plugins for langchain."""
from contextlib import ContextDecorator
from functools import wraps
from typing import Any, Callable

import pendulum
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult
from prefect import flow
from prefect import tags as prefect_tags
from prefect.utilities.asyncutils import is_async_fn
from prefect.utilities.collections import listrepr
from pydantic import BaseModel


class NotAnArtifact(BaseModel):
    """Placeholder class for soon-to-come `Artifact`."""

    name: str
    description: str
    content: Any


def llm_invocation_summary(*args, **kwargs) -> NotAnArtifact:
    """Will eventually return an artifact."""

    llm_endpoint = args[0].__module__
    text_input = listrepr(args[-1])

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


def record_llm_call(
    func: Callable[..., LLMResult],
    tags: set | None = None,
    flow_kwargs: dict | None = None,
):
    """Decorator for wrapping a Langchain LLM call with a prefect flow."""

    tags = tags or set()
    flow_kwargs = flow_kwargs or dict(name="Execute LLM Call", log_prints=True)

    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper for LLM calls"""
        invocation_artifact = llm_invocation_summary(*args, **kwargs)

        llm_endpoint, text_input, _ = invocation_artifact.content.values()
        tags.add(llm_endpoint)

        if is_async_fn(func):

            @flow(**flow_kwargs)
            async def execute_async_llm_call(
                text_input: str = text_input, llm_endpoint: str = llm_endpoint
            ):
                """async flow for async LLM calls via `SubclassofBaseLLM.agenerate`"""
                print(f"Sending {text_input} to {llm_endpoint}")
                llm_result: LLMResult = await func(*args, **kwargs)
                print(f"Recieved: {parse_llm_result(llm_result)}")
                return llm_result

            generate_fn = execute_async_llm_call
        else:

            @flow(**flow_kwargs)
            def execute_llm_call(
                text_input: str = text_input, llm_endpoint: str = llm_endpoint
            ):
                """sync flow for sync LLM calls via `SubclassofBaseLLM.generate`"""
                print(f"Sending {text_input} to {llm_endpoint}")
                llm_result: LLMResult = func(*args, **kwargs)
                print(f"Recieved: {parse_llm_result(llm_result)}")
                return llm_result

            generate_fn = execute_llm_call

        with prefect_tags(*tags):
            return generate_fn.with_options(
                flow_run_name=f"Calling {llm_endpoint} at {pendulum.now().strftime('%Y-%m-%d %H:%M:%S')})"  # noqa: E501
            )()

    return wrapper


class RecordLLMCalls(ContextDecorator):
    """Context manager for patching LLM calls with a prefect flow."""

    def __init__(self, **decorator_kwargs):
        """Initialize the context manager."""
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
