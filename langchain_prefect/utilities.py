"""Utilities for the langchain_prefect package."""

from typing import Any, Callable, List

import tiktoken
from langchain.schema import BaseMessage, LLMResult
from prefect import Flow, flow
from prefect.utilities.asyncutils import is_async_fn
from prefect.utilities.collections import listrepr
from pydantic import BaseModel


def get_prompt_content(prompts: Any) -> List[str]:
    """Return the content of the prompts."""
    if isinstance(prompts[0], str):
        return prompts
    elif isinstance(prompts[0], BaseMessage):
        return [p.content for p in prompts]
    else:
        return [p.content for msg_list in prompts for p in msg_list]


def num_tokens(text: str | List[str], encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    if isinstance(text, list):
        text = "".join(text)

    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens


def truncate(text: str, max_length: int = 300) -> str:
    """Truncate text to max_length."""
    if len(text) > 3 and len(text) >= max_length:
        i = (max_length - 3) // 2
        return f"{text[:i]}...{text[-i:]}"
    return text


class NotAnArtifact(BaseModel):
    """Placeholder class for soon-to-come `Artifact`."""

    name: str
    description: str
    content: Any


def llm_invocation_summary(*args, **kwargs) -> NotAnArtifact:
    """Will eventually return an artifact."""

    subcls, prompts, *rest = args

    invocation_fn = kwargs["invocation_fn"]

    llm_endpoint = subcls.__module__

    prompt_content = get_prompt_content(prompts)

    summary = (
        f"Sending {listrepr([truncate(p) for p in prompt_content])} "
        f"to {llm_endpoint} via {invocation_fn!r}"
    )

    return NotAnArtifact(
        name="LLM Invocation Summary",
        description=f"Query {llm_endpoint} via {invocation_fn.__name__}",
        content={
            "llm_endpoint": llm_endpoint,
            "prompts": prompts,
            "summary": summary,
            "args": rest,
            **kwargs,
        },
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
    flow_kwargs: dict | None = None,
    *args,
    **kwargs,
) -> Flow:
    """Define a function to be wrapped in a flow depending
    on whether the original function is sync or async."""
    flow_kwargs = flow_kwargs or dict(name="Execute LLM Call", log_prints=True)

    if is_async_fn(func):

        async def execute_async_llm_call(llm_input: NotAnArtifact) -> LLMResult:
            """async flow for async LLM calls via `SubclassofBaseLLM.agenerate`"""
            print(llm_input.content["summary"])
            llm_result = await func(*args, **kwargs)
            print(f"Recieved: {parse_llm_result(llm_result)!r}")
            return llm_result

        return flow(**flow_kwargs)(execute_async_llm_call)
    else:

        def execute_llm_call(llm_input: NotAnArtifact) -> LLMResult:
            """sync flow for sync LLM calls via `SubclassofBaseLLM.generate`"""
            print(llm_input.content["summary"])
            llm_result = func(*args, **kwargs)
            print(f"Recieved: {parse_llm_result(llm_result)!r}")
            return llm_result

        return flow(**flow_kwargs)(execute_llm_call)
