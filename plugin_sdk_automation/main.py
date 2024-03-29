import logging

import click
from rich.logging import RichHandler
from rich.traceback import install

from .handlers import DockerHandler
from .handlers import PropsHandler


install()


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
st = RichHandler()
fmt = logging.Formatter("%(filename)s:%(lineno)d - %(message)s")
st.setFormatter(fmt)
log.addHandler(st)


@click.group(invoke_without_command=True)
@click.option("--debug", default=False, is_flag=True)
@click.pass_context
def cli(ctx, debug):
    log.info(f"Debug is: {debug}")
    if debug:
        log.setLevel(logging.DEBUG)
    if ctx.invoked_subcommand is None:
        log.info("No subcommand provided, executing build")
        ctx.invoke(build)


@cli.command()
@click.option("--directory", "-d")
@click.option("--python-version", "-p", type=click.Choice(["py36", "py38"]))
def build(directory: str, python_version: str):
    d = DockerHandler(log=log, directory=directory, python_version=python_version)
    d.build()


@cli.command()
@click.option("--directory", "-d")
@click.option("--python-version", "-p", type=click.Choice(["py36", "py38"]))
@click.option("--os", "-o", type=click.Choice(["linux", "windows"]), default="linux")
def sim(directory: str, python_version: str, os: str):
    d = DockerHandler(log=log, directory=directory, python_version=python_version, simulator_os=os)
    d.sim()


@cli.command()
def gen_props():
    p = PropsHandler(log=log)
    p.run()


def main():
    cli()


if __name__ == "__main__":
    main()
