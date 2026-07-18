# Graph Orchestrator

This folder is the central nervous system of FinSight AI.

## Responsibilities
- **`graph_builder.py`**: Compiles the edges and nodes of the LangGraph state machine.
- **`workflow_runner.py`**: Wraps the graph execution, initializes the state with UUIDs, and triggers artifact bundling upon completion.
- **`nodes.py`**: Maps the core agent modules to the LangGraph node signatures.
