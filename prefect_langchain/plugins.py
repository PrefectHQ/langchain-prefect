"""Module for defining Prefect plugins for langchain."""

from functools import wraps
from typing import Any

from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult
from prefect import flow
from prefect.utilities.asyncutils import is_async_fn
from prefect.utilities.collections import listrepr
from pydantic import BaseModel


class NotAnArtifact(BaseModel):
    """Placeholder class for artifacts that are not yet implemented."""

    name: str
    description: str
    content: Any


def llm_invocation_summary(*args, **kwargs) -> NotAnArtifact:
    """Will eventually return an artifact."""
    llm_endpoint = str(args[0].client)
    text_input = listrepr(args[-1])

    return NotAnArtifact(
        name="LLM Invocation Summary",
        description="Summary of the LLM invocation.",
        content={"llm_endpoint": llm_endpoint, "text_input": text_input},
    )


def parse_llm_result(llm_result: LLMResult) -> NotAnArtifact:
    """Will eventually return an artifact."""
    output = listrepr([g[0].text.strip("\n") for g in llm_result.generations])
    token_usage = llm_result.llm_output["token_usage"]

    return NotAnArtifact(
        name="LLM Result",
        description="The result of the LLM invocation.",
        content={"output": output, "token_usage": token_usage},
    )


def record_llm_call(func):
    """Decorator for warpping LLM calls made by langchain with a prefect flow."""

    flow_kwargs = dict(name="Execute LLM Call", log_prints=True)

    if is_async_fn(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            """async wrapper for LLM calls"""
            invocation_artifact = llm_invocation_summary(*args, **kwargs)

            llm_endpoint, text_input = invocation_artifact.content.values()

            @flow(**flow_kwargs)
            async def execute_llm_call(llm_endpoint: str, text_input: str):
                """async flow for LLM calls"""
                print(f"Sending {text_input} to {llm_endpoint}")
                llm_result: LLMResult = await func(*args, **kwargs)

                result_artifact = parse_llm_result(llm_result)

                output, token_usage = result_artifact.content.values()

                print(f"Received output from LLM: {output}")
                print(f"Token Usage: {token_usage!r}")
                return llm_result

            return execute_llm_call(llm_endpoint, text_input)

    else:

        @wraps(func)
        def wrapper(*args, **kwargs):
            """sync wrapper for LLM calls"""
            invocation_artifact = llm_invocation_summary(*args, **kwargs)

            llm_endpoint, text_input = invocation_artifact.content.values()

            @flow(**flow_kwargs)
            def execute_llm_call(llm_endpoint: str, text_input: str):
                """async flow for LLM calls"""
                print(f"Sending {text_input} to {llm_endpoint}")
                llm_result: LLMResult = func(*args, **kwargs)

                result_artifact = parse_llm_result(llm_result)

                output, token_usage = result_artifact.content.values()

                print(f"Received output from LLM: {output}")
                print(f"Token Usage: {token_usage!r}")
                return llm_result

            return execute_llm_call(llm_endpoint, text_input)

    return wrapper


for cls in BaseLLM.__subclasses__():
    print(f"Wrapping {cls.__name__}")
    cls.agenerate = record_llm_call(cls.agenerate)
    cls.generate = record_llm_call(cls.generate)
