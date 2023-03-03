from prefect import flow

from prefect_langchain.tasks import (
    goodbye_prefect_langchain,
    hello_prefect_langchain,
)


def test_hello_prefect_langchain():
    @flow
    def test_flow():
        return hello_prefect_langchain()

    result = test_flow()
    assert result == "Hello, prefect-langchain!"


def goodbye_hello_prefect_langchain():
    @flow
    def test_flow():
        return goodbye_prefect_langchain()

    result = test_flow()
    assert result == "Goodbye, prefect-langchain!"
