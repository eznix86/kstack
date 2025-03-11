# Installation

kstack is a Python-based tool that requires Poetry for dependency management.

## Prerequisites

- Python 3.8 or later
- Poetry package manager
- Kubernetes cluster (for deployment)
- `kubectl` configured with cluster access

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/eznix86/kstack.git
cd kstack
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Verify installation:
```bash
poetry run kstack --version
```

## Next Steps

- Check out our [Quick Start Guide](quickstart.md) to deploy your first application
- Learn about [Basic Commands](commands.md) to manage your deployments
