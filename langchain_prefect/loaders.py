"""Loaders for Prefect."""
import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from typing import List

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from prefect.utilities.asyncutils import sync_compatible


class GitHubLoader(BaseLoader):
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
