import os
import signal
from os import popen

from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)
app.host = '0.0.0.0'
app.port = 42000


@app.post('/<service_name>')
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


@app.get("/stop/<service_name>")
def stop_service(service_name: str):
    print(popen(f'docker stop {service_name}'))


@app.get("/rmi/<full_image_name>")
def remove_image(full_image_name: str):
    docker_ps: str = popen('docker ps --filter "ancestor=' + full_image_name + '" --format "{{.ID}}?{{.Image}}"').read()
    if docker_ps != "":
        return Response(status=409)
    popen('docker rmi ' + full_image_name)


@app.get('/kill')
def kill():
    os.kill(os.getpid(), signal.SIGINT)
    return Response(
        'Server shutting down',
        status=200
    )


@app.get("/ping")
def ping():
    return Response(status=200)


if __name__ == '__main__':
    app.debug = True
    app.run(app.host, app.port)
