#!/usr/bin/env python3
import click
from rich.console import Console
from .actions import deploy_stack, validate_stack
from .utils import load_stack
from halo import Halo

console = Console()


@click.group()
def cli() -> None:
    """kstack - Deploy and manage Kubernetes clusters using simplified YAML."""
    pass


@cli.group()
def secret() -> None:
    """Commands to manage Kubernetes secrets."""
    pass


@cli.group()
def config() -> None:
    """Commands to manage Kubernetes configurations."""
    pass


@cli.command()
@click.argument("stack", type=click.Path(exists=True))
def deploy(stack: str) -> None:
    """Deploy resources defined in a kstack YAML file."""
    parsed_stack = load_stack(stack)

    if not validate_stack(parsed_stack, with_message=False):
        return

    deploy_stack(parsed_stack)


@cli.command()
@click.argument("stack", type=click.Path(exists=True))
def validate(stack: str) -> None:
    """Validate a kstack YAML file."""
    parsed_stack = load_stack(stack)
    validate_stack(parsed_stack)


@cli.command()
def destroy() -> None:
    """Destroy all resources defined in a kstack YAML file."""
    console.print("Hello, World!")


@secret.command()
def list() -> None:
    """List all Kubernetes secrets."""
    console.print("Hello, World!")


@secret.command()
def create() -> None:
    """Create a new Kubernetes secret."""
    console.print("Hello, World!")


@config.command()
def _list() -> None:
    """List all Kubernetes configurations."""
    console.print("Hello, World!")


@config.command()
def _create() -> None:
    """Create a new Kubernetes configuration."""
    console.print("Hello, World!")
