import os
import signal

from flask import Flask, Response, make_response
from flask_cors import CORS

from auth.Auth import Auth
from routes.ImageManager import image_routes
from routes.ServiceManager import docker

from routes.ServiceManager import service_routes

app = Flask(__name__)
CORS(app, support_credentials=True, resources={r"/*": {"origins": "*"}})
app.host = '0.0.0.0'
app.port = 42000

app.register_blueprint(service_routes)
app.register_blueprint(image_routes)


@app.get('/kill')
@Auth.requires_password
def kill():
    docker.close()
    os.kill(os.getpid(), signal.SIGINT)
    return Response(
        'Server shutting down',
        status=200
    )


@app.get("/ping")
@Auth.requires_password
def ping():
    return Response(status=200)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["OPTIONS"])
def prefligth(path):
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


@app.before_request
def login_ghcr():
    docker.login(
        os.environ.get("GITHUB_LOGIN"),
        os.environ.get("GITHUB_TOKEN"),
        registry="https://ghcr.io"
    )


if __name__ == '__main__':
    docker.login(
        os.environ.get("GITHUB_LOGIN"),
        os.environ.get("GITHUB_TOKEN"),
        registry="https://ghcr.io"
    )
    app.debug = True
    app.run(app.host, app.port)
