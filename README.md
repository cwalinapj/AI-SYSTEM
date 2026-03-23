# AI-SYSTEM

Agent Runtime, Unified Memory, Artifact Storage, Port Management agents, and expert agents.

## Architecture

The clean design is:

- OpenRouter for model inference
- your agent runtime for orchestration
- Postgres + pgvector for memory
- MinIO for scripts/artifacts
- an MCP gateway layer where you register local and remote MCP servers
- specialist agents that can use selected MCP servers based on domain

The MCP layer acts as the tool bus for the agent runtime. Each MCP server can expose:

- tools for actions
- resources for readable context
- prompts for reusable workflows

Copy `.env.example` to `.env` before running the stack. The example file uses clearly insecure placeholders for local setup only and must be replaced for any shared or production environment.

## Target Layout

```text
agent-system/
  docker-compose.yml
  .env
  .env.example

  mcp/
    registry/
      servers.yaml
      policies.yaml
    servers/
      port_manager/
      memory/
      scripts/
      luxonis/
      ml/
      filesystem/
      docker/
      github/
    gateway/
      router.py
      auth.py
      audit.py

  agent/
    app/
      orchestration/
      agents/
      memory/
      artifacts/
      execution/
      api/
```

## MCP Gateway Responsibilities

1. Register local and remote MCP servers from a shared registry.
2. Enforce per-agent capability scoping before tools or resources are exposed.
3. Route tool, resource, and prompt requests to the correct MCP server.
4. Audit which agent called which MCP capability and when.
5. Keep the agent runtime decoupled from individual server implementations.

## Starter MCP Servers

Core local servers:

- `memory`: search memories, write memory items, fetch procedures, retrieve similar incidents
- `scripts`: list scripts, fetch versions, register scripts, execute validated scripts
- `port_manager`: reserve/release ports, track leases, audit conflicts
- `filesystem`: provide controlled access to project files
- `docker`: inspect containers, list mapped ports, run validation containers

Specialist servers:

- `luxonis`: camera inventory, device status, calibration playbooks, DepthAI templates
- `ml`: dataset catalog, run history, training templates, evaluation reports
- `github`: repository automation and workflow context

## Capability Scoping

Agent policies should grant the minimum MCP surface area needed for the job:

- `generalist`: memory, scripts, filesystem, docker
- `port_manager`: port_manager, docker, filesystem
- `luxonis_expert`: memory, luxonis, scripts, docker
- `ml_expert`: memory, ml, scripts, filesystem

## Request Flow

```text
User
  -> Agent Router
     -> Generalist / Port / Luxonis / ML Expert
        -> MCP Gateway
           -> Memory MCP
           -> Script MCP
           -> Port Manager MCP
           -> Luxonis MCP
           -> ML MCP
           -> Filesystem MCP
           -> Docker MCP
           -> GitHub MCP
        -> OpenRouter model
        -> Postgres + pgvector
        -> MinIO
```

The first MCP servers to harden are memory, scripts, port management, docker, and luxonis. ML can follow once the core operational workflow is in place.
