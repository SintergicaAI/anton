import json
import mimetypes
from http.client import OK, NO_CONTENT, NOT_FOUND, CONFLICT
from urllib.error import HTTPError
from urllib.parse import unquote

from docker import DockerClient
from flask import Blueprint, Response, request

from auth.Auth import Auth

image_routes = Blueprint("image_routes", __name__, url_prefix="/image")
docker: DockerClient = DockerClient.from_env()


@image_routes.get("/")
@Auth.requires_password
def get_images():
    images = docker.images.list(all=True)
    if len(images) > 0:
        info: list = []
        for image in images:
            for tag in image.tags:
                info.append(tag)
        return Response(
            json.dumps(info),
            status=OK,
            mimetype=mimetypes.types_map[".json"]
        )
    return Response(status=NO_CONTENT)


@image_routes.delete("/")
@Auth.requires_password
def delete_image():
    full_image_name = unquote(request.args.get("image", default=""))
    try:
        image = docker.images.get(full_image_name)
        if is_image_used(full_image_name):
            return Response(status=CONFLICT)
        image.remove()
        print(f">>> Removed image {full_image_name}")
        return Response(status=OK)
    except HTTPError:
        print(">>> Image not found")
        return Response(status=NOT_FOUND)


def is_image_used(image_name: str) -> bool:
    for container in docker.containers.list():
        if image_name in container.image.tags:
            return True
    return False
