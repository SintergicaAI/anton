import os
import signal

from flask import Flask, Response, make_response
from flask_cors import CORS
from routes.ServiceManager import docker

from routes.ServiceManager import service_routes

app = Flask(__name__)
CORS(app, support_credentials=True)
app.host = '0.0.0.0'
app.port = 42000

app.register_blueprint(service_routes)


@app.get('/kill')
def kill():
    docker.close()
    os.kill(os.getpid(), signal.SIGINT)
    return Response(
        'Server shutting down',
        status=200
    )


@app.get("/ping")
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


if __name__ == '__main__':
    if os.environ.get("GITHUB_TOKEN") is None:
        raise Exception("GITHUB_TOKEN not found")
    app.debug = True
    app.run(app.host, app.port)
