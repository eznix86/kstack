"""Display manager for CLI output."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import yaml

class DisplayManager:
    def __init__(self):
        self.console = Console()

    def show_resources_table(self, resources):
        """Display table of generated resources."""
        table = Table(title="Generated Kubernetes Resources")
        table.add_column("Resource Type", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Kind", style="blue")
        table.add_column("Status", style="green")

        for resource_type, resource_list in resources.items():
            for resource in resource_list:
                name = resource['metadata']['name']
                kind = resource['kind']
                table.add_row(
                    resource_type,
                    name,
                    kind,
                    "✓"
                )

        self.console.print(table)

    def show_external_resources(self, compose_config):
        """Display information about external resources."""
        external_configs = []
        external_secrets = []

        # Collect external resources
        for service in compose_config.get('services', {}).values():
            if 'envFrom' in service:
                for env_from in service['envFrom']:
                    if 'config' in env_from and env_from['config'].get('external', False):
                        external_configs.append(env_from['config']['name'])
                    elif 'secret' in env_from and env_from['secret'].get('external', False):
                        external_secrets.append(env_from['secret']['name'])

        if external_configs or external_secrets:
            warning = Text()
            warning.append("\\nExternal Resources:\\n\\n", style="yellow")
            
            if external_configs:
                warning.append("ConfigMaps (must exist in cluster):\\n", style="yellow")
                for config in external_configs:
                    warning.append(f"  • {config}\\n")

            if external_secrets:
                warning.append("\\nSecrets (must exist in cluster):\\n", style="yellow")
                for secret in external_secrets:
                    warning.append(f"  • {secret}\\n")

            self.console.print(Panel(warning, title="Warning", border_style="yellow"))

    def show_dry_run_manifest(self, kind, name, namespace, data):
        """Display resource manifest for dry-run."""
        self.console.print(f"[yellow]{kind} manifest (dry-run):[/yellow]")
        manifest = {
            'apiVersion': 'v1',
            'kind': kind,
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'data': data
        }
        self.console.print(yaml.dump(manifest, default_flow_style=False))

    def show_skip_message(self, kind, name, namespace):
        """Display skip message for resource creation."""
        self.console.print(
            f"[yellow]Would create {kind} '{name}' in namespace '{namespace}' "
            "(skipped due to --skip-k8s-check)[/yellow]"
        )

    def show_success_message(self, kind, name, namespace):
        """Display success message for resource creation."""
        self.console.print(
            f"[green]✓ {kind} '{name}' created in namespace '{namespace}'[/green]"
        )
