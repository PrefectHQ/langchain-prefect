"""Module for defining Prefect plugins for langchain."""

from functools import wraps
from typing import Any, Dict, Tuple

from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult
from prefect import flow
from prefect.utilities.asyncutils import is_async_fn
from prefect.utilities.collections import listrepr


def llm_invocation_summary(*args, **kwargs) -> Tuple[str, str]:
    """Eventually an artifact."""
    llm_endpoint = str(args[0].client)
    text_input = listrepr(args[-1])

    return text_input, llm_endpoint


def parse_llm_result(llm_result: LLMResult) -> Tuple[str, Dict[str, Any]]:
    """Eventually an artifact."""
    output = listrepr([g[0].text.strip("\n") for g in llm_result.generations])
    token_usage = llm_result.llm_output["token_usage"]
    return output, token_usage


def record_llm_call(func):
    """Decorator for warpping LLM calls made by langchain with a prefect flow."""

    flow_kwargs = dict(name="Execute LLM Call", log_prints=True)

    if is_async_fn(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            """async wrapper for LLM calls"""
            text_input, llm_endpoint = llm_invocation_summary(*args, **kwargs)

            @flow(**flow_kwargs)
            async def execute_llm_call(llm_endpoint: str, text_input: str):
                """async flow for LLM calls"""
                print(f"Sending {text_input} to {llm_endpoint}")
                llm_result: LLMResult = await func(*args, **kwargs)
                print(llm_result)
                output = listrepr(
                    [g[0].text.strip("\n") for g in llm_result.generations]
                )
                print(f"Received output from LLM: {output}")
                print(f"Token Usage {llm_result.llm_output!r}")
                return llm_result

            return execute_llm_call(text_input, llm_endpoint)

    else:

        @wraps(func)
        def wrapper(*args, **kwargs):
            """sync wrapper for LLM calls"""
            llm_endpoint, text_input = llm_invocation_summary(*args, **kwargs)

            @flow(**flow_kwargs)
            def execute_llm_call(llm_endpoint: str, text_input: str):
                """async flow for LLM calls"""
                print(f"Sending {text_input} to {llm_endpoint}")
                llm_result: LLMResult = func(*args, **kwargs)
                print(llm_result)
                output = listrepr(
                    [g[0].text.strip("\n") for g in llm_result.generations]
                )
                print(f"Received output from LLM: {output}")
                print(f"Token Usage: {llm_result.llm_output!r}")
                return llm_result

            return execute_llm_call(text_input, llm_endpoint)

    return wrapper


for cls in BaseLLM.__subclasses__():
    print(f"Wrapping {cls.__name__}")
    cls.agenerate = record_llm_call(cls.agenerate)
    cls.generate = record_llm_call(cls.generate)
