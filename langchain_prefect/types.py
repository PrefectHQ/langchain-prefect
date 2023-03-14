from pydantic import BaseModel, Field
from typing import List


class GitHubUser(BaseModel):
    login: str


class GitHubComment(BaseModel):
    body: str = Field(default="")
    user: GitHubUser = Field(default_factory=GitHubUser)


class GitHubLabel(BaseModel):
    name: str = Field(default="")


class GitHubIssue(BaseModel):
    html_url: str = Field(...)
    number: int = Field(...)
    title: str = Field(default="")
    body: str | None = Field(default="")
    labels: List[GitHubLabel] = Field(default_factory=GitHubLabel)
    user: GitHubUser = Field(default_factory=GitHubUser)
