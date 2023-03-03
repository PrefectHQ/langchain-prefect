# prefect-langchain

<p align="center">
    <!--- Insert a cover image here -->
    <!--- <br> -->
    <a href="https://pypi.python.org/pypi/prefect-langchain/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect-langchain?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/zzstoatzz/prefect-langchain/" alt="Stars">
        <img src="https://img.shields.io/github/stars/zzstoatzz/prefect-langchain?color=0052FF&labelColor=090422" /></a>
    <a href="https://pypistats.org/packages/prefect-langchain/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/prefect-langchain?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/zzstoatzz/prefect-langchain/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/zzstoatzz/prefect-langchain?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect-community.slack.com" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.prefect.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
</p>

Visit the full docs [here](https://PrefectHQ.github.io/prefect-langchain) to see additional examples and the API reference.

Orchestrate and observe tools built with langchain.


<!--- ### Add a real-world example of how to use this Collection here

Offer some motivation on why this helps.

After installing `prefect-langchain` and [saving the credentials](#saving-credentials-to-block), you can easily use it within your flows to help you achieve the aforementioned benefits!

```python
from prefect import flow, get_run_logger
```

--->

## Resources

For more tips on how to use tasks and flows in a Collection, check out [Using Collections](https://docs.prefect.io/collections/usage/)!

### Installation

Install `prefect-langchain` with `pip`:

```bash
pip install prefect-langchain
```

Requires an installation of Python 3.7+.

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Prefect 2.0. For more information about how to use Prefect, please refer to the [Prefect documentation](https://docs.prefect.io/).

<!--- ### Saving credentials to block

Note, to use the `load` method on Blocks, you must already have a block document [saved through code](https://docs.prefect.io/concepts/blocks/#saving-blocks) or [saved through the UI](https://docs.prefect.io/ui/blocks/).

Below is a walkthrough on saving block documents through code.

1. Head over to <SERVICE_URL>.
2. Login to your <SERVICE> account.
3. Click "+ Create new secret key".
4. Copy the generated API key.
5. Create a short script, replacing the placeholders (or do so in the UI).

```python
from prefect_langchain import Block
Block(api_key="API_KEY_PLACEHOLDER").save("BLOCK_NAME_PLACEHOLDER")
```

Congrats! You can now easily load the saved block, which holds your credentials:

```python
from prefect_langchain import Block
Block.load("BLOCK_NAME_PLACEHOLDER")
```

!!! info "Registering blocks"

    Register blocks in this module to
    [view and edit them](https://docs.prefect.io/ui/blocks/)
    on Prefect Cloud:

    ```bash
    prefect block register -m prefect_langchain
    ```

A list of available blocks in `prefect-langchain` and their setup instructions can be found [here](https://PrefectHQ.github.io/prefect-langchain/blocks_catalog).

--->

### Feedback

If you encounter any bugs while using `prefect-langchain`, feel free to open an issue in the [prefect-langchain](https://github.com/zzstoatzz/prefect-langchain) repository.

If you have any questions or issues while using `prefect-langchain`, you can find help in either the [Prefect Discourse forum](https://discourse.prefect.io/) or the [Prefect Slack community](https://prefect.io/slack).

Feel free to star or watch [`prefect-langchain`](https://github.com/zzstoatzz/prefect-langchain) for updates too!

### Contributing

If you'd like to help contribute to fix an issue or add a feature to `prefect-langchain`, please [propose changes through a pull request from a fork of the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

Here are the steps:

1. [Fork the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
2. [Clone the forked repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
3. Install the repository and its dependencies:
```
pip install -e ".[dev]"
```
4. Make desired changes
5. Add tests
6. Insert an entry to [CHANGELOG.md](https://github.com/zzstoatzz/prefect-langchain/blob/main/CHANGELOG.md)
7. Install `pre-commit` to perform quality checks prior to commit:
```
pre-commit install
```
8. `git commit`, `git push`, and create a pull request
