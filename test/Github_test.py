import os
from time import sleep
from typing import Union

import pytest
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from github.Organization import Organization

from repo.GithubHandler import GithubHandler


@pytest.fixture(scope="module")
def handler():
    handler = GithubHandler(os.environ.get("GITHUB_TOKEN"))
    yield handler
    handler.github.close()
    print("Closing github connection")

@pytest.fixture(scope="module")
def org_name():
    return "SintergicaAI"

@pytest.fixture(scope="module")
def repository_name():
    return "test_repository"

@pytest.fixture(scope="module")
def user_name():
    return "GTWALOM"

def test_get_user(handler: GithubHandler, user_name: str):
    user: Union[NamedUser, AuthenticatedUser] = handler.github.get_user(user_name)
    assert user.login == user_name


def test_get_org(handler: GithubHandler, org_name):
    handler.set_org(org_name)
    org: Organization = handler.org
    assert org.login == org_name

def test_create_repository(handler: GithubHandler, repository_name: str, org_name: str):
    handler.set_org(org_name)
    assert handler.create_repository(repository_name)
    # Sleeping to make sure repository is reported as existing before next test
    sleep(1)

def test_repository_exists(handler: GithubHandler, repository_name: str, org_name: str):
    handler.set_org(org_name)
    assert handler.repository_exists(repository_name)

def test_delete_repository(handler: GithubHandler, repository_name: str, org_name: str):
    handler.set_org(org_name)
    assert not handler.delete_repository(repository_name)