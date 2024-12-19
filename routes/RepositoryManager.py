import os
from http.client import OK, CONFLICT, NOT_FOUND

from flask import Blueprint, Response

from repo.GithubHandler import GithubHandler

repository_routes = Blueprint('repository_routes', __name__, url_prefix="/repository")

handler: GithubHandler = GithubHandler(os.environ.get("GITHUB_TOKEN"))

@repository_routes.post("/<repository>")
def create_repository(repository: str):
    handler.set_org("SintergicaAI")
    if handler.create_repository(repository):
        return Response(status=OK)
    return Response(status=CONFLICT)


@repository_routes.delete("/<repository>")
def delete_repository(repository: str):
    handler.set_org("SintergicaAI")
    if handler.delete_repository(repository):
        return Response(status=OK)
    return Response(status=NOT_FOUND)