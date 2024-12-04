import pytest
import docker as dockerClient
from docker import DockerClient
from docker import errors


@pytest.fixture(scope="module")
def docker() -> DockerClient:
    print("Openning docker connection")
    docker_instance: DockerClient = dockerClient.from_env()
    yield docker_instance
    docker_instance.close()
    print("Closing docker connection")


@pytest.fixture(scope="module")
def image_name():
    return "alpine"


def test_pull_image(docker: DockerClient, image_name: str):
    docker.images.pull(image_name)
    assert docker.images.get(image_name) is not None


def test_image_exists(docker: DockerClient, image_name: str):
    assert docker.images.get(image_name) is not None


def test_run_container(docker: DockerClient, image_name: str):
    container = docker.containers.run(image_name, detach=True)
    assert container is not None
    container.stop()
    container.remove()


def test_remove_image(docker: DockerClient, image_name: str):
    try:
        docker.images.remove(image_name)
    except errors.ImageNotFound:
        pytest.fail("Image not found")
    try:
        docker.images.get(image_name)
    except errors.ImageNotFound:
        assert True
