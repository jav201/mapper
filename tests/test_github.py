"""Tests for mapper.github local-git connector."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from mapper.github import GitHubConnector, _is_local_path, _is_url


def test_is_url():
    assert _is_url("https://github.com/foo/bar.git")
    assert _is_url("git@github.com:foo/bar.git")
    assert not _is_url("foo/bar")
    assert not _is_url("/home/user/repo")


def test_is_local_path(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    assert _is_local_path(str(repo))
    assert not _is_local_path(str(tmp_path / "missing"))


def _git_init_commit(repo: Path, branch: str = "master") -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "README.md").write_text("# test", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init", "-q"], cwd=repo, check=True)


def test_fetch_local_repo(tmp_path):
    repo = tmp_path / "myrepo"
    repo.mkdir()
    _git_init_commit(repo)

    # Create a feature branch one commit ahead.
    subprocess.run(["git", "checkout", "-b", "feature", "-q"], cwd=repo, check=True)
    (repo / "feature.txt").write_text("feature", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "feature", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "checkout", "master", "-q"], cwd=repo, check=True)

    conn = GitHubConnector(str(repo))
    graph = conn.fetch()

    assert graph.root_id == "myrepo"
    assert "master" in graph.nodes
    assert "feature" in graph.nodes

    feature = graph.nodes["feature"]
    assert "+" in feature.ficha.meta and "-" in feature.ficha.meta


def test_fetch_local_repo_tags(tmp_path):
    repo = tmp_path / "tagged"
    repo.mkdir()
    _git_init_commit(repo)
    subprocess.run(["git", "tag", "v1.0"], cwd=repo, check=True)

    graph = GitHubConnector(str(repo)).fetch()
    assert graph.root_id == "tagged"
    assert "tags 1" in graph.nodes["tagged"].ficha.meta
