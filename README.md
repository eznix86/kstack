# kstack

kstack is a tool designed to simplify the deployment and management of Kubernetes clusters using a streamlined YAML configuration format. It abstracts complex Kubernetes configurations into a more user-friendly format, making it easier for developers and DevOps teams to manage their clusters.

## Features

- Simplified YAML configuration for Kubernetes resources.
- Support for deployments, services, ingresses, secrets, and volumes.
- Automatic validation of stack configurations against a JSON schema.
- CLI commands for deploying, validating, and managing Kubernetes resources.

## Installation

To install `kstack`, ensure you have Python 3.11 installed, then use `poetry` to install the dependencies:

```bash
poetry install
```

## Usage

### Validate a Stack

To validate a stack configuration file:

```bash
kstack validate examples/simple-deployment.yaml
```

### Deploy a Stack

To deploy resources defined in a stack configuration file:

```bash
kstack deploy examples/simple-deployment.yaml
```

### Destroy Resources

(Currently under development)

```bash
kstack destroy
```

## Example

Here is an example of a simple deployment configuration:

```yaml
apps:
    whoami:
        image: "containous/whoami"
        ports:
            - 8000:80
```

## Development

To contribute to `kstack`, clone the repository and install the dependencies using `poetry`:

```bash
git clone https://github.com/eznix86/kstack.git
cd kstack
poetry install
```

## License

kstack is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](./LICENSE) file for details.

