import logging
import docker
import time

from pathlib import Path


def make_posix_kitematic(directory: Path) -> str:
    # Convert path to windows/kitematic format
    # C:\Users\user > /c/Users/user
    directory = f"{directory.as_posix()}"
    if ":" in directory:
        drive, rest = directory.split(":", maxsplit=1)
        directory = f"{drive.lower()}{rest}"
        if not directory.startswith("/"):
            directory = f"/{directory}"
    return directory


def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    st = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s")
    st.setFormatter(fmt)
    log.addHandler(st)

    client = docker.from_env()

    log.info(f"Pulling the image")
    for log_line in client.api.pull("dlopes7/plugin_sdk", stream=True):
        log.info(log_line.decode().rstrip())

    # Check if we are where plugin.json is located
    if not Path("plugin.json") in list(Path().iterdir()):
        raise Exception("The command must be run from where plugin.json is located")

    current_dir = Path().absolute()
    build_dir = make_posix_kitematic(current_dir)
    parent_dir = make_posix_kitematic(current_dir.parents[0])

    volumes = {
        build_dir: {'bind': '/data/src', 'mode': 'rw'},
        parent_dir: {'bind': '/data', 'mode': 'rw'}
    }
    log.info(f"Will mount volumes: {volumes}")
    log.info(f"Starting docker container")

    start_time = time.time()

    # Remove fixme messages from output
    env = {"WINEDEBUG": "-all"}
    container = client.containers.run("dlopes7/plugin_sdk", volumes=volumes, remove=True, detach=True, environment=env)
    for log_line in container.logs(stdout=True, stderr=True, stream=True, follow=True):
        log.info(log_line.decode().rstrip())

    log.info(f"Docker container build finished after {time.time() - start_time:.2f}s")


if __name__ == '__main__':
    main()
