from typing import Union

from github import Auth
from github import Github
from github.Organization import Organization


class GithubHandler:
    def __init__(self, token: str):
        self.github = Github(auth=Auth.Token(token))
        self.org: Union[Organization, None] = None

    def __del__(self):
        self.github.close()

    def set_org(self, organization: str) -> None:
        self.org = self.github.get_organization(organization)

    def create_repository(self, repository: str) -> bool:
        if isinstance(self.org, Organization) and not self.repository_exists(repository):
            if self.org.create_repo(name=repository) is not None:
                return True
        return False

    def delete_repository(self, repository: str) -> bool:
        if isinstance(self.org, Organization) and self.repository_exists(repository):
            self.org.get_repo(repository).delete()
            return True
        return False

    def repository_exists(self, repository: str) -> bool:
        repositories = self.github.search_repositories(query=self.org.login + "/" + repository)
        return repositories.totalCount > 0
