# langchain-prefect

<p align="center">
    <!--- Insert a cover image here -->
    <!--- <br> -->
    <img src="https://user-images.githubusercontent.com/31014960/224118318-02e49d8e-72e0-4850-93f7-d850c0f06ca1.png">
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

Read the [accompanying article](https://medium.com/the-prefect-blog/keeping-your-eyes-on-your-ai-tools-6428664537da) for background

## Orchestrate and observe langchain using Prefect

Large Language Models (LLMs) are interesting and useful  -  building apps that use them responsibly feels like a no-brainer. Tools like [Langchain](https://github.com/hwchase17/langchain) make it easier to build apps using LLMs. We need to know details about how our apps work, even when we want to use tools with convenient abstractions that may obfuscate those details.

Prefect is built to help data people build, run, and observe event-driven workflows wherever they want. It provides a framework for creating deployments on a whole slew of runtime environments (from Lambda to Kubernetes), and is cloud agnostic (best supports AWS, GCP, Azure). For this reason, it could be a great fit for observing apps that use LLMs.

## Features
- `RecordLLMCalls` is a `ContextDecorator` that can be used to track LLM calls made by Langchain LLMs as Prefect flows.

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

<p align="center">
    <img src="https://user-images.githubusercontent.com/31014960/224114166-f2c7d5ed-49b6-406e-a384-bd327d4e1fe4.png" alt="LLM invocation UI">
</p>

### Run several LLM calls via langchain agent as Prefect subflows:
```python
from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI

from prefect import flow

llm = OpenAI(temperature=0)
tools = load_tools(["llm-math"], llm=llm)
agent = initialize_agent(tools, llm)

@flow
def my_flow():
    agent.run(
        "How old is the current Dalai Lama? "
        "What is his age divided by 2 (rounded to the nearest integer)?"
    )

with RecordLLMCalls(tags={"agent"}):
    my_flow()
```

<p align="center">
    <img src="https://user-images.githubusercontent.com/31014960/224113843-b91f204b-8085-4739-b483-a45c4f339210.png" alt="LLM agent UI">
</p>

Find more examples [here](examples/).

## How do I get a Prefect UI?
- The easiest way is to use the [Prefect Cloud](https://www.prefect.io/cloud/) UI for free. You can find details on getting setup [here](https://docs.prefect.io/ui/cloud-quickstart/).

- If you don't want to sign up for cloud, you can use the dashboard locally by running `prefect server start` in your terminal - more details [here](https://docs.prefect.io/ui/overview/#using-the-prefect-ui).


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
