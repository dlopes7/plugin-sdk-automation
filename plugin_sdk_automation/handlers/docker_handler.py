import shutil
import time
import logging
from pathlib import Path

import docker

from plugin_sdk_automation.handlers.props_handler import PropsHandler


def check_plugin_json_exists():
    if not Path("plugin.json") in list(Path().iterdir()):
        raise Exception("psa must be run from where plugin.json is located")


class DockerHandler:
    def __init__(self, log: logging.Logger, directory=None, python_version=None, simulator_os="linux"):
        self.log = log
        self.directory = directory
        self.docker_client = docker.from_env()

        if python_version is None:
            python_version = "py38"
        self.python_version = python_version
        self.simulator_os = simulator_os

    def _pull_image(self):
        image_name = f"dlopes7/plugin_sdk:{self.python_version}"
        self.log.info(f"Pulling the image '{image_name} if necessary'")
        for log_line in self.docker_client.api.pull(image_name, stream=True):
            self.log.info(log_line.decode().rstrip())

    def _create_volumes(self):
        current_dir = Path().absolute()
        build_dir = make_posix_kitematic(current_dir)
        if self.directory:
            parent_dir = Path(self.directory).resolve()
        else:
            parent_dir = make_posix_kitematic(current_dir.parents[0])

        volumes = {build_dir: {"bind": "/data/src", "mode": "rw"}, parent_dir: {"bind": "/data", "mode": "rw"}}
        self.log.info(f"Will mount volumes: {volumes}")
        return volumes

    def build(self):
        check_plugin_json_exists()
        self._pull_image()

        self.log.info(f"Starting docker container")
        start_time = time.time()

        env = {"WINEDEBUG": "-all", "PYTHON_SHORT_VERSION": self.python_version.replace("py", "")}
        container = self.docker_client.containers.run(
            f"dlopes7/plugin_sdk:{self.python_version}", volumes=self._create_volumes(), remove=True, detach=True, environment=env
        )
        for log_line in container.logs(stdout=True, stderr=True, stream=True, follow=True):
            self.log.info(log_line.decode().rstrip())

        self.log.info(f"Docker container build finished after {time.time() - start_time:.2f}s.")

    def _create_properties_if_needed(self):
        p = PropsHandler(self.log)
        if Path("properties.json") not in list(Path().iterdir()):
            p.run()

    def sim(self):

        check_plugin_json_exists()
        self._create_properties_if_needed()

        self._pull_image()

        self.log.info(f"Starting docker container")
        start_time = time.time()

        if self.simulator_os == "linux":
            command = "oneagent_simulate_plugin -p /data/src"
        else:
            command = f"wine64 /python/python{self.python_version.replace('py', '')}/Scripts/oneagent_simulate_plugin.exe -p /data/src"

        env = {"WINEDEBUG": "-all", "PYTHON_SHORT_VERSION": self.python_version.replace("py", "")}
        container = self.docker_client.containers.run(
            f"dlopes7/plugin_sdk:{self.python_version}",
            volumes=self._create_volumes(),
            remove=True,
            detach=True,
            environment=env,
            command=command,
        )
        for log_line in container.logs(stdout=True, stderr=True, stream=True, follow=True):
            self.log.info(log_line.decode().rstrip())

        self.log.info(f"Docker container build finished after {time.time() - start_time:.2f}s.")


def make_posix_kitematic(directory: Path) -> str:
    directory = f"{directory.as_posix()}"
    if ":" in directory:
        drive, rest = directory.split(":", maxsplit=1)
        directory = f"{drive.lower()}{rest}"
        if not directory.startswith("/"):
            directory = f"/{directory}"
    return directory
