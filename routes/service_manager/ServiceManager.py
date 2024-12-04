from os import popen

from flask import Blueprint, request, Response

service_routes = Blueprint("service_routes", __name__, url_prefix="/service")


@service_routes.route("/<service_name>")
def set_service(service_name: str):
    image_to_pull: str = request.args.get("image")
    tag: str = request.args.get("tag")
    iport: str = request.args.get("iport")
    eport: str = request.args.get("eport")
    privileged: bool = request.args.get("privileged") == "1"
    variables: dict = request.json

    get_container_id: str = 'docker ps --filter "name=' + service_name + '" --format "{{.ID}}?{{.Image}}"'

    print(popen(f'docker pull {image_to_pull}:{tag}').read())
    response: list = popen(get_container_id).read().replace("\n", "").split("?")
    print(response)

    if len(response) == 2:
        container_id: str = response[0]
        image_to_delete: str = response[1]

        print(popen(f'docker stop {container_id}').read())
        print(popen(f'docker rmi {image_to_delete}').read())

    run: str = f'docker run -d --rm --name {service_name} -p {eport}:{iport}'
    if privileged:
        run += ' --privileged'
    for key, value in variables.items():
        run += f" --env {key}='{value}'"
    run += f' {image_to_pull}:{tag}'

    print(run)

    print(popen(run).read())
    return Response(status=200)

@service_routes.get("/stop/<service_name>")
def stop_service(service_name: str):
    print(popen(f'docker stop {service_name}'))

@service_routes.get("/rmi/<full_image_name>")
def remove_image(full_image_name: str):
    docker_ps: str = popen('docker ps --filter "ancestor=' + full_image_name + '" --format "{{.ID}}?{{.Image}}"').read()
    if docker_ps != "":
        return Response(status=409)
    popen('docker rmi ' + full_image_name)