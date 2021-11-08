import shutil
import time
import logging
from pathlib import Path

import docker


class DockerHandler:
    def __init__(self, log: logging.Logger, directory=None, python_version=None):
        self.log = log
        self.directory = directory
        
        if python_version is None:
            python_version = "py38"
        self.python_version = python_version

    def build(self):
        client = docker.from_env()

        # Check if we are where plugin.json is located

        if not Path("plugin.json") in list(Path().iterdir()):
            raise Exception("psa must be run from where plugin.json is located")

        image_name = f"dlopes7/plugin_sdk:{self.python_version}"
        self.log.info(f"Pulling the image '{image_name}'")
        for log_line in client.api.pull(image_name, stream=True):
            self.log.info(log_line.decode().rstrip())

        current_dir = Path().absolute()
        build_dir = make_posix_kitematic(current_dir)
        if self.directory:
            parent_dir = Path(self.directory).resolve()
        else:
            parent_dir = make_posix_kitematic(current_dir.parents[0])
        dist_folder = Path(parent_dir, "dist")

        volumes = {build_dir: {"bind": "/data/src", "mode": "rw"}, parent_dir: {"bind": "/data", "mode": "rw"}}
        self.log.info(f"Will mount volumes: {volumes}")
        self.log.info(f"Starting docker container")

        start_time = time.time()

        env = {"WINEDEBUG": "-all"}
        container = client.containers.run("dlopes7/plugin_sdk", volumes=volumes, remove=True, detach=True, environment=env)
        for log_line in container.logs(stdout=True, stderr=True, stream=True, follow=True):
            self.log.info(log_line.decode().rstrip())

        self.log.info(f"Docker container build finished after {time.time() - start_time:.2f}s. Extension deployed to {dist_folder}")


def make_posix_kitematic(directory: Path) -> str:
    directory = f"{directory.as_posix()}"
    if ":" in directory:
        drive, rest = directory.split(":", maxsplit=1)
        directory = f"{drive.lower()}{rest}"
        if not directory.startswith("/"):
            directory = f"/{directory}"
    return directory
