import os

from flask import Blueprint, Response

from repo.GithubHandler import GithubHandler

repository_routes = Blueprint('repository_routes', __name__, url_prefix="/repository")

handler: GithubHandler = GithubHandler(os.environ.get("GITHUB_TOKEN"))

@repository_routes.post("/repository/<repository>")
def create_repository(repository: str):
    handler.set_org("SintergicaAI")
    if handler.create_repository(repository):
        return Response(status=200)
    return Response(status=409)


@repository_routes.delete("/repository/<repository>")
def delete_repository(repository: str):
    handler.set_org("SintergicaAI")
    if handler.delete_repository(repository):
        return Response(status=200)
    return Response(status=404)