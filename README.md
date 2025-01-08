# ASTRA AI FRAMEWORK

## AI-powered framework for efficient on-chain infrastructure. Unified gateways, smart validators, and adaptive automation for seamless scalability and precision

## Contract address: `ASTRATQVDx4yscfDaqgemypwzzK37Qq8j7jvPGsbhmY1`
## X: https://x.com/astraframework
## HUB: https://t.me/astraframework
## Web: https://astragateways.ai/

## What is astra?
### Framework Components

### AstraAI streamlines on-chain operations with three integrated components:

### /Gateways and Nodes: Unified to manage high-speed data flow while maintaining the distributed ledger. This combination ensures scalability and adaptable configurations for seamless network functionality.

### /Validators: Verify transactions, secure the network, and utilize AI-powered monitoring to optimize performance in real-time.
### /AI Agent: Acts as the system's brain, automating routine tasks, predicting network demands, and dynamically allocating resources for efficiency
## Quick start

You can choose either to either install via [pip] or [Docker] (recommended). Refer to  
[our technical documentation][install] for full usage instructions.

## Development

Ensure you have Python 3.6+ installed. Again, we recommend that you use a `virtualenv` for `astragateway` development.

Clone the `astracommon` repo, which contains abstract interfaces for the gateway node's event loop, connection management, 
and message classes that are shared with other astra nodes.

```bash
git clone https://github.com/astra-Labs/astracommon.git
```

Make sure `astracommon/src` is in your `PYTHONPATH` and export some environment variables (you can also add this to your
`~/.bash_profile`, or however you prefer to manage your environment).

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/astracommon/src 
export DYLD_LIBRARY_PATH="/usr/local/opt/openssl@1.1/lib"  # for OpenSSL dependencies
```

Install dependencies:

```bash
pip install -r astracommon/requirements.txt
pip install -r astracommon/requirements-dev.txt
pip install -r astragateway/requirements.txt
pip install -r astragateway/requirements-dev.txt
```

Run unit and integration tests:

```bash
cd astragateway/test
python -m unittest discover
```

Run `astragateway` from source:

```bash
cd astragateway/src/astragateway
python main.py --blockchain-network [blockchain-network] --blockchain-protocol [blockchain-protocol]
```

### Extensions
`astragateway` has references to C++ extensions for faster performance on CPU intensive operations. To make use of this, 
clone the `astraextensions` repository, build the source files, and add the entire `astraextensions` folder to your 
`PYTHONPATH`.

```bash
git clone --recursive https://github.com/astra-Labs/astraextensions.git
```

Refer to [astraextensions] for information on building the C++ extensions.

## Documentation

You can find our full technical documentation and architecture [on our website][documentation].

## Troubleshooting

Contact us at support@astra.com for further questions.

