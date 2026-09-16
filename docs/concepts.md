# Core concepts

## The execution loop

The agent sends context and tool descriptions to a model. The model returns text or tool calls. The engine executes permitted tools, adds their results to the conversation, and calls the model again until completion or a limit.

A tool is application code. A model's decision to call it does not replace input validation, authorization or business rules in that code.

## Three levels of control

**`ask` and `stream`** are convenient one-shot functions. They own a short-lived agent and close it when finished.

**`Agent`** owns a conversation, tool registry, model client, repository and engine. It initializes its repository lazily. Use an async context manager to close it reliably.

**`AgentEngine`** accepts explicitly constructed components and middleware. Initialize the repository before using it. Use this level when integrating with an existing application lifecycle.

## Definitions and instances

`AgentDefinition` declares a name, model, system prompt, tools and limits. Its `tools` list contains registered names. `Agent` accepts functions directly and registers them for you. Lower-level callers construct a `ToolRegistry` themselves.

The `Agent` facade can auto-detect a model from configured providers. A lower-level `AgentDefinition` should receive an explicit model: the facade's convenience detection is not a promise that every API picks a default.

## Sessions and storage

A session identifies a conversation and its history. Reusing a session ID continues it. The engine serializes runs for a session within that engine instance; this is not a distributed lock across independent processes.

Memory storage disappears with the process. SQLite stores locally. PostgreSQL supports shared durable storage, but application deployment still owns database migrations, credentials, pooling and cross-process coordination.

## Results and events

`Agent.run()` returns final text, a session ID and collected events. Streaming yields events as they happen: text deltas, tool activity, errors and lifecycle changes. Keep structured events if you need to explain what an agent did.

## What the SDK does not decide

Your application chooses model access, authorized tools, tenant identity, data retention, idempotency and spending policy. A tool timeout does not prove that an external write was canceled. Use application-owned request IDs and reconciliation for consequential operations.
