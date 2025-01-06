import json
import mimetypes
from http.client import OK, NOT_FOUND, CONFLICT
from typing import Optional, Union

import docker as dockerClient
from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image
from flask import Blueprint, request, Response
from requests import HTTPError

from auth.Auth import Auth

service_routes = Blueprint("service_routes", __name__, url_prefix="/service")
docker: DockerClient = dockerClient.from_env()


@service_routes.get("/")
@Auth.requires_password
def get_services():
    info: list = []
    containers: list[Container] = docker.containers.list(all=True)
    for container in containers:
        info.append({
            "name": container.name,
            "image": container.image.id,
            "tag": container.image.tags[0],
            "status": container.status
        })
    return Response(
        json.dumps(info),
        status=OK,
        mimetype=mimetypes.types_map[".json"]
    )


@service_routes.post("/<service_name>")
@Auth.requires_password
def set_service(service_name: str):
    image_to_pull: str = request.args.get("image")
    tag: str = request.args.get("tag")
    iport: str = request.args.get("iport")
    eport: str = request.args.get("eport")
    ivol: str = request.args.get("ivol", default=None)
    evol: str = request.args.get("evol", default=None)
    privileged: bool = request.args.get("privileged", default="0") == "1"
    variables: dict = request.json

    if is_eport_used(eport):
        return Response(status=CONFLICT)

    image_to_remove: Optional[Image] = None

    if image_already_downloaded(image_to_pull, tag):
        image = docker.images.get(image_to_pull + ":" + tag)
    else:
        image = docker.images.pull(image_to_pull, tag=tag)

    try:
        running_container: Container = docker.containers.get(service_name)
        image_to_remove = running_container.image

        running_container.stop()
        running_container.remove()
        print(f">>> Container {running_container.id} removed")
    except HTTPError:
        print(">>> No container found. Running new instance")

    new_container: Container = docker.containers.run(
        image,
        name=service_name,
        detach=True,
        privileged=privileged,
        ports={iport: eport},
        environment=variables,
        volumes=get_volumes_config(evol, ivol),
        remove=True
    )

    print(f">>> Container {new_container.id} | {new_container.image} created")

    if image_to_remove is not None and image_to_remove.id != image.id:
        image_to_remove.remove()

    return Response(status=OK)


@service_routes.delete("/<service_name>")
@Auth.requires_password
def stop_service(service_name: str):
    container = docker.containers.get(service_name)
    container.stop()
    container.remove()
    print(">>> Stopped container")
    return Response(status=OK)


@service_routes.delete("/rmi/<full_image_name>")
@Auth.requires_password
def remove_image(full_image_name: str):
    if docker.images.get(full_image_name) is not None:
        docker.images.remove(full_image_name)
        print(f">>> Removed image {full_image_name}")
        return Response(status=OK)
    return Response(status=NOT_FOUND)


def image_already_downloaded(image_name: str, tag: str) -> bool:
    for container in docker.containers.list():
        if container.image.tags[0] == image_name + ":" + tag:
            return True
    return False


def is_eport_used(port: Union[int, str]) -> bool:
    if isinstance(port, int):
        port = str(port)
    for container in docker.containers.list():
        _, item = container.ports.popitem()
        if item[0]["HostPort"] == port:
            return True
    return False


def get_volumes_config(evol: Union[str, None], ivol: Union[str, None]) -> Union[dict, None]:
    if evol is not None and ivol is not None:
        return {evol: {'bind': ivol, 'mode': 'rw'}}
    return None
