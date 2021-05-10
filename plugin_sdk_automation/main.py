import logging

import click
from plugin_sdk_automation.handlers import DockerHandler
from rich.logging import RichHandler
from rich.traceback import install

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
def build(directory: str):
    d = DockerHandler(log=log, directory=directory)
    d.build()


def main():

    cli()


if __name__ == "__main__":
    main()
