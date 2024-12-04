from typing import Optional

import docker as dockerClient
from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image
from flask import Blueprint, request, Response

service_routes = Blueprint("service_routes", __name__, url_prefix="/service")
docker: DockerClient = dockerClient.from_env()


@service_routes.post("/<service_name>")
def set_service(service_name: str):
    image_to_pull: str = request.args.get("image")
    tag: str = request.args.get("tag")
    iport: str = request.args.get("iport")
    eport: str = request.args.get("eport")
    privileged: bool = request.args.get("privileged") == "1"
    variables: dict = request.json

    new_image: Image = docker.images.pull(image_to_pull, tag=tag)
    image_to_remove: Optional[Image] = None

    try:
        running_container: Container = docker.containers.get(service_name)
        image_to_remove = running_container.image

        running_container.stop()
        running_container.remove()
        print(f">>> Container {running_container.id} removed")
    except docker.errors.NotFound:
        print(">>> No container found. Running new instance")

    new_container: Container = docker.containers.run(
        new_image,
        name=service_name,
        detach=True,
        privileged=privileged,
        ports={iport: eport},
        environment=variables
    )

    print(f">>> Container {new_container.id} | {new_container.image} created")

    if image_to_remove is not None:
        image_to_remove.remove()

    return Response(status=200)


@service_routes.delete("/stop/<service_name>")
def stop_service(service_name: str):
    docker.containers.get(service_name).stop()
    print(">>> Stopped container")
    return Response(status=200)


@service_routes.delete("/rmi/<full_image_name>")
def remove_image(full_image_name: str):
    if docker.images.get(full_image_name) is not None:
        docker.images.remove(full_image_name)
        print(f">>> Removed image {full_image_name}")
        return Response(status=200)
    return Response(status=404)
