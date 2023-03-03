"""This is an example flows module"""
from prefect import flow

from prefect_langchain.blocks import LangchainBlock
from prefect_langchain.tasks import (
    goodbye_prefect_langchain,
    hello_prefect_langchain,
)


@flow
def hello_and_goodbye():
    """
    Sample flow that says hello and goodbye!
    """
    LangchainBlock.seed_value_for_example()
    block = LangchainBlock.load("sample-block")

    print(hello_prefect_langchain())
    print(f"The block's value: {block.value}")
    print(goodbye_prefect_langchain())
    return "Done"


if __name__ == "__main__":
    hello_and_goodbye()
