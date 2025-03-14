from jsonschema import Draft202012Validator, validate, ValidationError
import os.path as path
import json
import halo
from rich.console import Console
from functools import reduce
from .transformers import (
    to_deployments,
    to_loadbalancers,
    to_ingresses,
    to_persistent_volume_claim,
)
from kubernetes import config
from .deployments import apply_deployments, apply_services, apply_ingresses, apply_persistent_volume_claims

console = Console()


def deploy_stack(stack: dict, namespace: str = "default") -> None:
    transformers_steps = [
        to_persistent_volume_claim,
        to_loadbalancers,
        to_deployments,
        to_ingresses,
    ]

    manifests = reduce(
        lambda manifests, func: func(stack, manifests), transformers_steps, []
    )

    config.load_kube_config()

    deployment_steps = [apply_persistent_volume_claims, apply_services, apply_deployments, apply_ingresses]

    manifests = reduce(
        lambda manifests, func: func(manifests, namespace), deployment_steps, manifests
    )


def validate_stack(stack: dict, with_message: bool = True) -> bool:
    spinner = halo.Halo(
        text="validating stack...", spinner="dots", enabled=with_message
    )
    spinner.start()

    schema_file = path.join(path.dirname(__file__), "kstack.schema.json")

    with open(schema_file) as f:
        schema = json.load(f)

        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(stack), key=lambda e: e.path)

        if errors:
            spinner.fail("Validation failed")
            console.print(
                "[bold red]The stack configuration contains errors:[/bold red]"
            )
            for error in errors:
                error_path = ".".join(map(str, error.path)) if error.path else "root"
                console.print(
                    f"  [bold yellow]{error_path}[/bold yellow]: {error.message}"
                )
            return False

        spinner.succeed("Stack is valid")

    return True
