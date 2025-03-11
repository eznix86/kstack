"""CLI interface for kstack."""
import click
from .commands import CommandHandlers

@click.group()
def cli():
    """kstack - Convert Docker Compose to Kubernetes resources."""
    pass

@cli.command(name='get-context')
def get_context():
    """Show current Kubernetes context information."""
    CommandHandlers.handle_get_context()

@cli.group()
def create():
    """Create Kubernetes resources."""
    pass

@create.command()
@click.argument('name')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--from-env-file', type=click.Path(exists=True), help='Load from env file')
@click.option('--from-literal', multiple=True, help='Key-value pair in KEY=VALUE format')
@click.option('--skip-k8s-check', is_flag=True, help='Skip Kubernetes connection check')
@click.option('--dry-run', is_flag=True, help='Print the resource instead of creating it')
def secret(name, namespace, from_env_file, from_literal, skip_k8s_check, dry_run):
    """Create a Kubernetes secret."""
    CommandHandlers.handle_create_secret(name, namespace, from_env_file, from_literal, skip_k8s_check, dry_run)

@create.command()
@click.argument('name')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--from-env-file', type=click.Path(exists=True), help='Load from env file')
@click.option('--from-literal', multiple=True, help='Key-value pair in KEY=VALUE format')
@click.option('--skip-k8s-check', is_flag=True, help='Skip Kubernetes connection check')
@click.option('--dry-run', is_flag=True, help='Print the resource instead of creating it')
def config(name, namespace, from_env_file, from_literal, skip_k8s_check, dry_run):
    """Create a Kubernetes ConfigMap."""
    CommandHandlers.handle_create_config(name, namespace, from_env_file, from_literal, skip_k8s_check, dry_run)

@cli.command()
@click.argument('compose_file', type=click.Path(exists=True), required=False)
@click.option('-f', '--file', type=click.Path(exists=True), help='Docker Compose file')
@click.option('--output-dir', '-o', default='./k8s', help='Output directory for Kubernetes manifests')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--skip-k8s-check', is_flag=True, help='Skip Kubernetes connection check')
def convert(compose_file, file, output_dir, namespace, skip_k8s_check):
    """Convert a compose file to Kubernetes manifests."""
    target_file = file or compose_file
    if not target_file:
        raise click.UsageError("Please provide a compose file either as an argument or with -f/--file option")
    CommandHandlers.handle_convert(target_file, output_dir, namespace, skip_k8s_check)

@cli.command()
@click.argument('compose_file', type=click.Path(exists=True), required=False)
@click.option('-f', '--file', type=click.Path(exists=True), help='Docker Compose file')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--skip-k8s-check', is_flag=True, help='Skip Kubernetes connection check')
def apply(compose_file, file, namespace, skip_k8s_check):
    """Apply a compose file to Kubernetes cluster."""
    target_file = file or compose_file
    if not target_file:
        raise click.UsageError("Please provide a compose file either as an argument or with -f/--file option")
    CommandHandlers.handle_apply(target_file, namespace, skip_k8s_check)

@cli.command()
@click.argument('compose_file', type=click.Path(exists=True), required=False)
@click.option('-f', '--file', type=click.Path(exists=True), help='Docker Compose file')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--skip-k8s-check', is_flag=True, help='Skip Kubernetes connection check')
def validate(compose_file, file, namespace, skip_k8s_check):
    """Validate a compose file and check external resources."""
    target_file = file or compose_file
    if not target_file:
        raise click.UsageError("Please provide a compose file either as an argument or with -f/--file option")
    CommandHandlers.handle_validate(target_file, namespace, skip_k8s_check)

@cli.command()
@click.argument('compose_file', type=click.Path(exists=True), required=False)
@click.option('-f', '--file', type=click.Path(exists=True), help='Docker Compose file')
@click.option('--namespace', '-n', default='default', help='Kubernetes namespace')
@click.option('--skip-k8s-check', is_flag=True, help='Skip Kubernetes connection check')
@click.option('--force', is_flag=True, help='Force deletion without confirmation')
def destroy(compose_file, file, namespace, skip_k8s_check, force):
    """Delete all Kubernetes resources created from the compose file."""
    target_file = file or compose_file
    if not target_file:
        raise click.UsageError("Please provide a compose file either as an argument or with -f/--file option")
    CommandHandlers.handle_destroy(target_file, namespace, skip_k8s_check, force)

if __name__ == '__main__':
    cli()
