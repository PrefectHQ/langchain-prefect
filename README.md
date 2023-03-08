# langchain-prefect

<p align="center">
    <!--- Insert a cover image here -->
    <!--- <br> -->
    <a href="https://pypi.python.org/pypi/langchain-prefect/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/langchain-prefect?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/PrefectHQ/langchain-prefect/" alt="Stars">
        <img src="https://img.shields.io/github/stars/PrefectHQ/langchain-prefect?color=0052FF&labelColor=090422" /></a>
    <a href="https://pypistats.org/packages/langchain-prefect/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/langchain-prefect?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/PrefectHQ/langchain-prefect/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/PrefectHQ/langchain-prefect?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect-community.slack.com" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.prefect.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
</p>

Orchestrate and observe tools built with langchain using Prefect.



## Example Usage

### Call an LLM and track the invocation with Prefect:
```python
from langchain.llms import OpenAI
from langchain_prefect.plugins import RecordLLMCalls

with RecordLLMCalls():
    llm = OpenAI(temperature=0.9)
    text = (
        "What would be a good company name for a company that makes colorful socks?"
    )
    llm(text)
```
and a flow run will be created to track the invocation of the LLM:

![](docs/img/LLMinvokeUI.png)

### Run several LLM calls via langchain agent as Prefect subflows:
```python
from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI

from prefect import flow

llm = OpenAI(temperature=0)
tools = load_tools(["llm-math"], llm=llm)
agent = initialize_agent(tools, llm)

@flow
def my_flow():  # noqa: D103
    agent.run(
        "How old is the current Dalai Lama? "
        "What is his age divided by 2 (rounded to the nearest integer)?"
    )

with RecordLLMCalls(tags={"agent"}):
    my_flow()
```
![](docs/img/LLMagentUI.png)

Find more examples [here](examples/).

## Resources
### Installation

```bash
pip install langchain-prefect
```

Requires an installation of Python 3.10+.

### Feedback

If you encounter any bugs while using `langchain-prefect`, feel free to open an issue in the [langchain-prefect](https://github.com/PrefectHQ/langchain-prefect) repository.

Feel free to star or watch [`langchain-prefect`](https://github.com/PrefectHQ/langchain-prefect) for updates too!

### Contributing

If you'd like to help contribute to fix an issue or add a feature to `langchain-prefect`, please [propose changes through a pull request from a fork of the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

Here are the steps:

1. [Fork the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
2. [Clone the forked repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
3. Install the repository and its dependencies:
```
pip install -e ".[dev]"
```
4. Make desired changes
5. Add tests
6. Insert an entry to [CHANGELOG.md](https://github.com/PrefectHQ/langchain-prefect/blob/main/CHANGELOG.md)
7. Install `pre-commit` to perform quality checks prior to commit:
```
pre-commit install
```
8. `git commit`, `git push`, and create a pull request
