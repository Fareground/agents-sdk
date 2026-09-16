# Agents SDK

**Build agents with tools, conversations and streaming in Python.**

The Agents SDK (`fg-agents`) provides a simple entry point for a model-backed assistant, plus lower-level control over tools, persistence, middleware and web integration.

[Run your first agent →](getting-started.md) · [Tools](tools.md) · [API reference](api.md)

## Choose the right starting point

| Need | API | Guide |
|---|---|---|
| One answer | `ask()` | [Quickstart](getting-started.md) |
| A conversation with tools | `Agent` | [Core concepts](concepts.md) |
| Incremental output | `stream()` or `Agent.stream()` | [Streaming](streaming.md) |
| Durable conversations | SQLite or PostgreSQL repository | [Persistence](persistence.md) |
| Custom hooks and execution control | `AgentEngine` | [Tools and middleware](tools.md) |
| Coordinated specialists | `Orchestrator` | [Skills and orchestration](orchestration.md) |
| An HTTP service | `create_app` or `create_agent_router` | [Web integration](web.md) |

## Install

```bash
python -m pip install "fg-agents[anthropic]"
```

Python 3.11 or later. Install the extra for your provider or integration. These pages describe **0.4.1**; check `fg_agents.__version__` in your installed environment.

## Relationship to the Environments SDK

The [Environments SDK](https://fareground.com/docs/env-kernel/) defines and executes simulation rules. The Agents SDK runs an agent's reasoning and tools. They are independent packages. Use the environment's participant interface when connecting an agent; do not let the agent bypass the environment's rules.

[GitHub](https://github.com/Fareground/agents-sdk) · [PyPI](https://pypi.org/project/fg-agents/) · [Migration](migration.md) · [Apache-2.0](https://github.com/Fareground/agents-sdk/blob/main/LICENSE)
