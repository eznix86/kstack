"""Command handlers for the CLI."""
import click
from rich.console import Console
from kubernetes import client
import base64
import yaml
from ..core.context import KubernetesContext
from ..core.resource_manager import ResourceManager
from ..parsers.compose_parser import ComposeParser
from ..generators.kube_generator import KubeResourceGenerator
from .display import DisplayManager

console = Console()
display = DisplayManager()

class CommandHandlers:
    @staticmethod
    def handle_get_context():
        """Show current Kubernetes context information."""
        try:
            KubernetesContext.validate_connection()
        except Exception as e:
            console.print(f"[red]{str(e)}[/red]")
            raise click.Abort()

    @staticmethod
    def handle_create_secret(name, namespace, from_env_file, from_literal, skip_k8s_check, dry_run):
        """Handle secret creation command."""
        try:
            if not (skip_k8s_check or dry_run):
                KubernetesContext.validate_connection()
            
            # Create secret using ResourceManager
            resource_mgr = ResourceManager(namespace)
            secret_data = resource_mgr.create_secret_data(from_env_file, from_literal)
            
            if dry_run:
                display.show_dry_run_manifest('Secret', name, namespace, secret_data)
            elif skip_k8s_check:
                display.show_skip_message('Secret', name, namespace)
            else:
                resource_mgr.apply_secret(name, secret_data)
                display.show_success_message('Secret', name, namespace)
                
        except Exception as e:
            console.print(f"[red]Error creating secret: {str(e)}[/red]")
            raise click.Abort()

    @staticmethod
    def handle_create_config(name, namespace, from_env_file, from_literal, skip_k8s_check, dry_run):
        """Handle ConfigMap creation command."""
        try:
            if not (skip_k8s_check or dry_run):
                KubernetesContext.validate_connection()
            
            # Create ConfigMap using ResourceManager
            resource_mgr = ResourceManager(namespace)
            config_data = resource_mgr.create_config_data(from_env_file, from_literal)
            
            if dry_run:
                display.show_dry_run_manifest('ConfigMap', name, namespace, config_data)
            elif skip_k8s_check:
                display.show_skip_message('ConfigMap', name, namespace)
            else:
                resource_mgr.apply_config_map(name, config_data)
                display.show_success_message('ConfigMap', name, namespace)
                
        except Exception as e:
            console.print(f"[red]Error creating ConfigMap: {str(e)}[/red]")
            raise click.Abort()

    @staticmethod
    def handle_convert(compose_file, output_dir, namespace, skip_k8s_check):
        """Handle compose file conversion command."""
        try:
            if not skip_k8s_check:
                KubernetesContext.validate_connection()
            
            # Parse and generate resources
            parser = ComposeParser(compose_file, namespace, skip_k8s_check=skip_k8s_check)
            compose_config = parser.parse()
            generator = KubeResourceGenerator(compose_config, namespace)
            resources = generator.generate_all()
            
            # Save resources if output_dir is specified
            if output_dir:
                generator.save_to_files(resources, output_dir)
            
            # Display results
            display.show_resources_table(resources)
            display.show_external_resources(compose_config)
            
            return resources
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            raise click.Abort()

    @staticmethod
    def handle_apply(compose_file, namespace, skip_k8s_check):
        """Handle compose file application command."""
        try:
            # First convert the compose file
            resources = CommandHandlers.handle_convert(
                compose_file, None, namespace, skip_k8s_check
            )
            
            if not skip_k8s_check:
                # Apply resources using ResourceManager
                resource_mgr = ResourceManager(namespace)
                resource_mgr.apply_resources(resources)
                console.print(f"\n[green]✓ Successfully applied resources to namespace '{namespace}'[/green]")
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            raise click.Abort()

    @staticmethod
    def handle_validate(compose_file, namespace, skip_k8s_check):
        """Handle compose file validation command."""
        try:
            if not skip_k8s_check:
                KubernetesContext.validate_connection()
            
            # Parse and validate compose file
            parser = ComposeParser(compose_file, namespace, skip_k8s_check=skip_k8s_check)
            compose_config = parser.parse()
            
            # Display external resources that need to exist
            display.show_external_resources(compose_config)
            console.print("[green]✓ Compose file is valid[/green]")
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            raise click.Abort()

    @staticmethod
    def handle_destroy(compose_file, namespace, skip_k8s_check, force):
        """Handle compose file resource deletion command."""
        try:
            if not skip_k8s_check:
                KubernetesContext.validate_connection()
            
            # Parse and generate resources
            parser = ComposeParser(compose_file, namespace, skip_k8s_check=skip_k8s_check)
            compose_config = parser.parse()
            generator = KubeResourceGenerator(compose_config, namespace)
            resources = generator.generate_all()
            
            # Show resources to be deleted
            display.show_resources_table(resources)
            
            # Get confirmation unless --force is used
            if not force:
                if not click.confirm('\nAre you sure you want to delete these resources?'):
                    console.print('\nAborted!')
                    return
            
            # Delete resources in reverse order to handle dependencies
            resource_mgr = ResourceManager(namespace)
            resource_mgr.delete_resources(resources)
            
            console.print(f"\n[green]✓ Successfully deleted resources from namespace '{namespace}'[/green]")
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            raise click.Abort()
