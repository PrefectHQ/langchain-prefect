"""Loaders for Prefect."""
import asyncio
import httpx
import os
import shutil
import tempfile
from pathlib import Path
from typing import List

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain_prefect.types import GitHubComment, GitHubIssue
from prefect.utilities.asyncutils import sync_compatible


class GithubIssueLoader(BaseLoader):
    """Loader for GitHub issues for a given repository."""

    def __init__(self, repo: str, n_issues: int):
        """
        Initialize the loader with the given repository.

        Args:
            repo: The name of the repository, in the format "<owner>/<repo>"
        """
        self.repo = repo
        self.n_issues = n_issues
        self.request_headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        # If a GitHub token is available, use it to increase the rate limit
        if token := os.environ.get("GITHUB_TOKEN"):
            self.request_headers["Authorization"] = f"Bearer {token}"

    def _get_issue_comments(
        self, issue_number: int, per_page: int = 100
    ) -> List[GitHubComment]:
        """
        Get a list of all comments for the given issue.

        Returns:
            A list of dictionaries, each representing a comment.
        """
        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}/comments"
        comments = []
        page = 1
        while True:
            response = httpx.get(
                url=url,
                headers=self.request_headers,
                params={"per_page": per_page, "page": page},
            )
            response.raise_for_status()
            if not (new_comments := response.json()):
                break
            comments.extend([GitHubComment(**comment) for comment in new_comments])
            page += 1
        return comments

    def _get_issues(self, per_page: int = 100) -> List[GitHubIssue]:
        """
        Get a list of all issues for the given repository.

        Returns:
            A list of `GitHubIssue` objects, each representing an issue.
        """
        url = f"https://api.github.com/repos/{self.repo}/issues"
        issues = []
        page = 1
        while True:
            if len(issues) >= self.n_issues:
                break
            remaining = self.n_issues - len(issues)
            response = httpx.get(
                url=url,
                headers=self.request_headers,
                params={
                    "per_page": remaining if remaining < per_page else per_page,
                    "page": page,
                    "include": "comments",
                },
            )
            response.raise_for_status()
            if not (new_issues := response.json()):
                break
            issues.extend([GitHubIssue(**issue) for issue in new_issues])
            page += 1
        return issues

    def load(self) -> List[Document]:
        """
        Load all issues for the given repository.

        Returns:
            A list of `Document` objects, each representing an issue.
        """
        issues = self._get_issues()
        documents = []
        for issue in issues:
            text = f"{issue.title}\n{issue.body}"
            if issue.comments:
                for comment in self._get_issue_comments(issue.number):
                    text += f"\n\n{comment.user.login}: {comment.body}\n\n"
            metadata = {
                "source": issue.html_url,
                "title": issue.title,
                "labels": ",".join([label.name for label in issue.labels]),
            }
            documents.append(Document(page_content=text, metadata=metadata))
        return documents


class GitHubRepoLoader(BaseLoader):
    """Loader for files on GitHub that match a glob pattern."""

    def __init__(self, repo: str, glob: str):
        """Initialize with the GitHub repository and glob pattern.

        Attrs:
            repo: The organization and repository name, e.g. "prefecthq/prefect"
            glob: The glob pattern to match files, e.g. "**/*.md"

        """
        self.repo = f"https://github.com/{repo}.git"
        self.glob = glob

    @sync_compatible
    async def load(self) -> List[Document]:
        """Load files from GitHub that match the glob pattern."""
        tmp_dir = tempfile.mkdtemp()
        try:
            process = await asyncio.create_subprocess_exec(
                *["git", "clone", "--depth", "1", self.repo, tmp_dir]
            )
            if (await process.wait()) != 0:
                raise OSError(
                    f"Failed to clone repository:\n {process.stderr.decode()}"
                )

            # Read the contents of each file that matches the glob pattern
            documents = []
            for file in Path(tmp_dir).glob(self.glob):
                with open(file, "r") as f:
                    text = f.read()

                metadata = {
                    "source": os.path.join(self.repo, file.relative_to(tmp_dir))
                }
                documents.append(Document(page_content=text, metadata=metadata))

            return documents
        finally:
            shutil.rmtree(tmp_dir)
