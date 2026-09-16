# Public API reference

Generated from public exports in `fg_agents`. See [API guide](api.md) for common workflows.

## `ask`

```python
ask(prompt: str, *, model: str | None = None, tools: list[collections.abc.Callable | fg_agents.core.types.RegisteredTool] | None = None, system_prompt: str = '', memory: str | fg_agents.persistence.base.BaseRepository = 'memory', **kwargs) -> fg_agents.agent.AgentRunResult
```

Ask a one-shot question and get the final answer.

Example::

    from fg_agents import ask

    print(await ask("What's 2+2?"))

Args:
    prompt: The user message.
    model: Provider-qualified model id (``"anthropic:claude-sonnet-4-6"``).
        Omit to auto-detect from the environment.
    tools: Tools available to the agent (``@tool`` functions, plain
        callables, or ``RegisteredTool`` instances).
    system_prompt: System prompt for the run.
    memory: Persistence backend — ``"memory"`` (default), ``"sqlite[:path]"``,
        ``"postgres:<url>"``, or a ready repository.
    **kwargs: Everything else :class:`~fg_agents.Agent` accepts
        (``api_keys``, ``max_turns``, ``temperature``, ...).

Returns:
    :class:`~fg_agents.AgentRunResult` — ``str()`` of it is the answer
    text, so ``print(await ask(...))`` prints just the answer.

## `stream`

```python
stream(prompt: str, *, model: str | None = None, tools: list[collections.abc.Callable | fg_agents.core.types.RegisteredTool] | None = None, system_prompt: str = '', memory: str | fg_agents.persistence.base.BaseRepository = 'memory', **kwargs) -> collections.abc.AsyncIterator[fg_agents.streaming.events.StreamEvent]
```

One-shot question, streamed: yields :class:`StreamEvent` s as they happen.

Example::

    from fg_agents import stream

    async for event in stream("Tell me a story"):
        print(event.type, event.data)

Accepts the same arguments as :func:`ask`. The ephemeral agent is
closed when the stream is exhausted or the generator's ``aclose()``
runs. If you may exit early (``break``/``return`` mid-iteration), wrap
the stream so cleanup is deterministic rather than left to garbage
collection::

    import contextlib

    async with contextlib.aclosing(stream("Tell me a story")) as events:
        async for event in events:
            if enough(event):
                break

## `resolve_default_model`

```python
resolve_default_model() -> str
```

Pick a default provider-qualified model id from the environment.

Detection order: ``ANTHROPIC_API_KEY`` → ``OPENAI_API_KEY`` →
``GOOGLE_API_KEY``/``GEMINI_API_KEY`` → local Ollama on port 11434.
The Ollama probe blocks briefly; in async code prefer
:func:`resolve_default_model_async`. The probe result is cached for a
short interval.

Raises:
    ModelDetectionError: nothing detected — set one of the env vars,
        run Ollama locally, or pass ``model=`` explicitly.

## `resolve_default_model_async`

```python
resolve_default_model_async() -> str
```

Async twin of :func:`resolve_default_model` — same detection order and
error, but the Ollama probe uses a non-blocking connection so the event
loop is never stalled. Used by ``ask()``/``stream()``.

## `ModelDetectionError`

Raised when no model was given and none could be detected.

## `Agent`

```python
Agent(model: str | None = None, *, tools: list[collections.abc.Callable | fg_agents.core.types.RegisteredTool] | None = None, system_prompt: str = '', name: str = 'agent', memory: str | fg_agents.persistence.base.BaseRepository = 'memory', llm: fg_agents.core.llm.AgentLLM | None = None, api_keys: dict[str, str] | None = None, session_id: str | None = None, **agent_kwargs)
```

High-level facade over AgentLLM, ToolRegistry, a repository, and AgentEngine.

Args:
    model: Provider-qualified model id, e.g. ``"anthropic:claude-sonnet-4-6"``.
        When omitted (``None``), a default is detected from the
        environment — see :func:`fg_agents.resolve_default_model` for
        the detection order.
    tools: Tools available to the agent. Accepts ``@tool``-decorated
        functions, plain callables (auto-wrapped via ``@tool``), or
        ``RegisteredTool`` instances.
    system_prompt: System prompt for the agent.
    name: Agent name (defaults to ``"agent"``).
    memory: Persistence backend — ``"memory"`` (default), ``"sqlite"``,
        ``"sqlite:<path>"``, or a ready :class:`BaseRepository` instance.
    llm: Optional pre-built :class:`AgentLLM` (e.g. with api_keys).
    api_keys: Provider → API key overrides (ignored when ``llm`` is given).
    session_id: Conversation id. Defaults to a fresh id per Agent
        instance; every run/stream continues the same conversation
        unless a per-call ``session_id`` is passed.
    **agent_kwargs: Extra :class:`AgentDefinition` fields passed through
        (``max_turns``, ``temperature``, ``fallback_models``, ...).

Initialization is lazy: the repository is initialized on the first
``run``/``stream`` call — forgetting to initialize is never an error.

## `AgentRunError`

```python
AgentRunError(message: str, session_id: str, events: list[fg_agents.streaming.events.StreamEvent])
```

Raised by :meth:`Agent.run` when a run fails.

Carries the session id and the partial events collected before the
failure. The original exception (if any) is chained as ``__cause__``.

## `AgentRunResult`

```python
AgentRunResult(text: str, session_id: str, events: list[fg_agents.streaming.events.StreamEvent] = <factory>) -> None
```

Result of a completed :meth:`Agent.run` call.

## `AgentSession`

```python
AgentSession(*, id: str = <factory>, agent_id: str = '', user_id: str = '', tenant_id: str = '', parent_session_id: str | None = None, status: fg_agents.core.types.SessionStatus = <SessionStatus.IDLE: 'idle'>, config: dict[str, typing.Any] = <factory>, metadata: dict[str, typing.Any] = <factory>, created_at: datetime.datetime = <factory>, updated_at: datetime.datetime = <factory>, completed_at: datetime.datetime | None = None, total_input_tokens: int = 0, total_output_tokens: int = 0, total_cost_usd: float = 0.0, turn_count: int = 0, error: str | None = None) -> None
```

Top-level container for an agent run, scoped to a user and tenant.

## `AgentMessage`

```python
AgentMessage(*, id: str = <factory>, session_id: str = '', role: fg_agents.core.types.MessageRole, content: str | list[dict[str, typing.Any]] = '', tool_calls: list[fg_agents.core.types.ToolCall] | None = None, tool_call_id: str | None = None, tool_name: str | None = None, token_count: int = 0, model: str | None = None, created_at: datetime.datetime = <factory>, is_summarized: bool = False) -> None
```

A single message in the conversation.

## `AgentDefinition`

```python
AgentDefinition(*, id: str = <factory>, name: str, description: str = '', objective: str = '', system_prompt: str = '', model: str = '', fallback_models: list[str] = <factory>, tools: list[str] = <factory>, skills: list[str] = <factory>, knowledge: list[typing.Any] = <factory>, max_turns: int = 50, max_llm_retries: int = 3, min_turns: int = 0, require_explicit_completion: bool = False, max_tokens_per_turn: int = 8192, llm_timeout_seconds: float = 120.0, nudge_after_seconds: int = 180, hard_deadline_seconds: int = 600, temperature: float = 0.0, middleware: list[str] = <factory>, sub_agents: dict[str, fg_agents.core.types.AgentDefinition] = <factory>, max_parallel_agents: int = 5, memory_scope: str = 'isolated', extra_context: str = '', metadata: dict[str, typing.Any] = <factory>) -> None
```

Declarative agent configuration.

Defines everything an agent needs: model, tools, skills, prompts,
knowledge files, sub-agents it can spawn, and constraints.

## `ToolCall`

```python
ToolCall(*, id: str = <factory>, tool_name: str, arguments: dict[str, typing.Any] = <factory>, arguments_error: str | None = None) -> None
```

A tool invocation requested by the LLM.

## `ToolResult`

```python
ToolResult(*, tool_call_id: str, tool_name: str, output: Any = None, status: fg_agents.core.types.ToolStatus = <ToolStatus.SUCCESS: 'success'>, duration_ms: float = 0.0, error: str | None = None) -> None
```

The result of executing a tool.

## `ToolSchema`

```python
ToolSchema(*, name: str, description: str, parameters: dict[str, typing.Any] = <factory>) -> None
```

LLM-facing tool definition — the JSON Schema the model sees.
Provider adapters convert this to Anthropic/OpenAI/etc format.

## `RegisteredTool`

```python
RegisteredTool(*, name: str, description: str, tool_type: fg_agents.core.types.ToolType = <ToolType.FUNCTION: 'function'>, parameters: list[fg_agents.core.types.ToolParameterSpec] = <factory>, json_schema: dict[str, typing.Any] = <factory>, config: dict[str, typing.Any] = <factory>, requires_auth: bool = False, permission_level: str = 'auto_approve', timeout_seconds: int = 30, retry_max: int = 0, tags: list[str] = <factory>, handler: typing.Any | None = None) -> None
```

A tool registered in the ToolRegistry.

## `Skill`

```python
Skill(*, id: str = <factory>, name: str, version: str = '1.0', description: str = '', prompt_template: str = '', required_tools: list[str] = <factory>, config: dict[str, typing.Any] = <factory>, tags: list[str] = <factory>) -> None
```

Reusable agent capability = prompt template + required tools + config.

Skills are injected into the system prompt when activated.
They can define which tools are needed, and provide Jinja2 templates
with variables resolved at runtime.

## `ExecutionContext`

```python
ExecutionContext(*, session_id: str = '', agent_id: str = '', agent_name: str = '', turn_number: int = 0, parent_session_id: str | None = None, user_id: str = '', tenant_id: str = '', metadata: dict[str, typing.Any] = <factory>, working_memory: typing.Any | None = None, repository: typing.Any | None = None, active_skills: list[typing.Any] = <factory>) -> None
```

Runtime context available to tools, middleware, and hooks.
Carries session info, agent definition, auth context, and references to services.

Auth fields (user_id, tenant_id) are pass-throughs from your web app.
The framework never handles auth — your app authenticates, then passes
the identity here so tools, middleware, and persistence are scoped correctly.

## `SubAgentResult`

```python
SubAgentResult(*, child_session_id: str, output: str = '', data: dict[str, typing.Any] = <factory>, status: fg_agents.core.types.ToolStatus = <ToolStatus.SUCCESS: 'success'>, error: str | None = None, turns_used: int = 0, tokens_used: fg_agents.core.types.LLMUsage = <factory>) -> None
```

Result returned by a sub-agent to its parent.

## `UserContext`

```python
UserContext(*, user_id: str = '', tenant_id: str = '', org_id: str = '', metadata: dict[str, typing.Any] = <factory>) -> None
```

User/tenant context passed through from the web app.

The framework never handles auth — your app does. This is the
pass-through context that scopes sessions, messages, and memory
to the right user and tenant.

## `LLMStreamChunk`

```python
LLMStreamChunk(*, type: str, text: str | None = None, tool_call: fg_agents.core.types.ToolCall | None = None, tool_call_id: str | None = None, tool_name: str | None = None, arguments_delta: str | None = None, usage: fg_agents.core.types.LLMUsage | None = None, stop_reason: fg_agents.core.types.StopReason | None = None) -> None
```

A single chunk from a streaming LLM response.

## `LLMResponse`

```python
LLMResponse(*, content: str = '', tool_calls: list[fg_agents.core.types.ToolCall] = <factory>, stop_reason: fg_agents.core.types.StopReason = <StopReason.END_TURN: 'end_turn'>, usage: fg_agents.core.types.LLMUsage = <factory>, model: str = '', latency_ms: float = 0.0) -> None
```

Complete (non-streaming) LLM response.

## `LLMUsage`

```python
LLMUsage(*, input_tokens: int = 0, output_tokens: int = 0, cache_creation_tokens: int = 0, cache_read_tokens: int = 0, total_tokens: int = 0) -> None
```

Token usage from an LLM call.

## `SessionStatus`

```python
SessionStatus(value, names=None, *, module=None, qualname=None, type=None, start=1, boundary=None)
```

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

## `MessageRole`

```python
MessageRole(value, names=None, *, module=None, qualname=None, type=None, start=1, boundary=None)
```

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

## `ToolStatus`

```python
ToolStatus(value, names=None, *, module=None, qualname=None, type=None, start=1, boundary=None)
```

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

## `ToolType`

```python
ToolType(value, names=None, *, module=None, qualname=None, type=None, start=1, boundary=None)
```

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

## `EventType`

```python
EventType(value, names=None, *, module=None, qualname=None, type=None, start=1, boundary=None)
```

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

## `StopReason`

```python
StopReason(value, names=None, *, module=None, qualname=None, type=None, start=1, boundary=None)
```

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

## `AgentLLM`

```python
AgentLLM(api_keys: dict[str, str] | None = None, custom_providers: dict[str, str] | None = None)
```

Provider-agnostic LLM interface with streaming and tool-use support.

Supports 20+ providers out of the box via OpenAI-compatible API.
Lazily initializes provider clients. Thread-safe via asyncio.Lock.

## `AgentEngine`

```python
AgentEngine(llm: fg_agents.core.llm.AgentLLM, tool_registry: fg_agents.tools.registry.ToolRegistry, repository: fg_agents.persistence.base.BaseRepository, skills_manager: fg_agents.skills.manager.SkillsManager | None = None, middleware: list[fg_agents.middleware.base.BaseMiddleware] | None = None)
```

The ReAct agent loop engine.

Orchestrates: LLM calls → tool execution → message persistence → streaming.
Stateless between runs — all state lives in the repository.

Session locking: Only one run() can execute per session_id at a time.
Concurrent requests to the same session wait in line.

## `Orchestrator`

```python
Orchestrator(llm: fg_agents.core.llm.AgentLLM, tool_registry: fg_agents.tools.registry.ToolRegistry, repository: fg_agents.persistence.base.BaseRepository, skills_manager: fg_agents.skills.manager.SkillsManager | None = None, middleware: list[fg_agents.middleware.base.BaseMiddleware] | None = None, auto_register_builtins: bool = True)
```

The brain agent. Plans, delegates to sub-agents, synthesizes results.

This is the top-level entry point for running agents in this system.
It manages:
- The core AgentEngine (ReAct loop)
- Sub-agent registration and delegation
- Built-in tools (manage_agent, manage_knowledge, manage_plan, etc.)
- Default middleware (audit, token tracking)
- Skill resolution

The orchestrator wires the manage_agent tool to the SubAgentRunner,
so when the LLM calls manage_agent, it actually spawns a sub-agent.

## `SubAgentRunner`

```python
SubAgentRunner(engine: fg_agents.core.engine.AgentEngine)
```

Spawn and manage sub-agents with isolated context.

Design:
- Each sub-agent creates a CHILD session in DB (linked via parent_session_id)
- Sub-agent gets a fresh message history — only the task description + optional context
- Runs its own ReAct loop via the shared AgentEngine
- Returns ONLY the final result to the parent (full conversation persisted in child)
- All intermediate reasoning stays isolated (auditable via child session)
- Optional on_event callback streams events in real-time (e.g. to WebSocket)

## `ToolRegistry`

```python
ToolRegistry(vault_resolver=None)
```

Central tool store with execution capabilities.

Tools can be registered via:
1. @tool decorated functions (have .tool_definition attribute)
2. RegisteredTool instances directly
3. Dictionaries with tool config

Execution handles timeout, retry, and error wrapping.

## `tool`

```python
tool(name: str | None = None, description: str | None = None, tool_type: fg_agents.core.types.ToolType = <ToolType.FUNCTION: 'function'>, permission_level: str = 'auto_approve', timeout_seconds: int = 30, retry_max: int = 0, tags: list[str] | None = None, json_schema: dict[str, typing.Any] | None = None) -> collections.abc.Callable
```

Decorator to register a function as an agent tool.

Usage:
    @tool(name="search_db", description="Search the case database")
    async def search_db(query: str, limit: int = 10, ctx: ExecutionContext) -> dict:
        results = await do_search(query, limit)
        return {"results": results}

The decorated function gains a `.tool_definition` attribute containing
the RegisteredTool instance, which can be added to a ToolRegistry.

The JSON schema is inferred from the signature: type hints map to JSON
types (str/int/float/bool/list/dict, Optional unwrapped), defaults are
recorded and make a parameter optional, and per-parameter descriptions
are pulled from a Google-style ``Args:`` docstring section when present.
A plain type-hinted function needs nothing more.

Parameters named 'ctx' or 'context' with type ExecutionContext are
automatically injected by the framework — they don't appear in the
tool's JSON schema.

## `dispatch_tool`

```python
dispatch_tool(tool_def: fg_agents.core.types.RegisteredTool, tool_call: fg_agents.core.types.ToolCall, context: fg_agents.core.types.ExecutionContext, vault_resolver: typing.Any | None = None) -> fg_agents.core.types.ToolResult
```

Dispatch a tool call to the appropriate handler based on tool_type.

For FUNCTION tools, the handler is called directly (via ToolRegistry).
For other types, the appropriate handler from this module is used.

## `SkillsManager`

```python
SkillsManager(repository: fg_agents.persistence.base.BaseRepository | None = None)
```

Manages skill definitions — loading, resolution, and prompt injection.

Skills are composable prompt templates + tool requirements.
They tell the agent HOW to do something specific.

## `WorkingMemory`

```python
WorkingMemory(session_id: str = '', metadata: dict | None = None)
```

In-process working memory for an agent session.

Stores intermediate data, tool results, findings, and metadata
that the agent accumulates during execution. This is the fast
scratchpad — session-scoped, not persisted to DB.

The context manager pattern ensures working memory is available
during the agent run and cleaned up after.

## `ContextManager`

```python
ContextManager(repository: fg_agents.persistence.base.BaseRepository, trigger_fraction: float = 0.8, keep_recent_fraction: float = 0.15, custom_context_limits: dict[str, int] | None = None)
```

Manages the conversation context to fit within model limits.

Strategy:
1. Load messages from DB for the session
2. Estimate total tokens
3. If > trigger_threshold (default 80% of limit):
   a. Layer 1: Truncate old tool arguments
   b. Layer 2: Auto-summarize old messages, keeping recent ones
4. Return optimized message list for the LLM call

## `Middleware`

```python
Middleware(*args, **kwargs)
```

Protocol for agent loop middleware.

Implement any subset of these methods. Unimplemented methods
default to pass-through (return inputs unchanged).

## `BaseMiddleware`

```python
BaseMiddleware()
```

Convenience base class implementing pass-through for all hooks.
Subclass and override only the methods you need.

## `AuditMiddleware`

```python
AuditMiddleware(repository: fg_agents.persistence.base.BaseRepository)
```

Logs every significant action to the af_audit_log table.

Captures:
- LLM calls (model, tokens, latency)
- Tool executions (name, status, duration)
- Errors
- Turn completions

## `TokenTrackingMiddleware`

```python
TokenTrackingMiddleware(repository: fg_agents.persistence.base.BaseRepository)
```

Tracks cumulative token usage and cost for each session.
Updates the session record in DB after each LLM call.

## `PermissionMiddleware`

```python
PermissionMiddleware(rules: list[fg_agents.middleware.permissions.PermissionRule] | None = None, default_level: str = 'auto_approve', denied_tools: list[str] | None = None, approval_callback=None)
```

Enforces tool permission rules.

Rules are evaluated in order — first match wins.
If no rule matches, the default level applies.

## `PermissionRule`

```python
PermissionRule(tool_pattern: str, level: str = 'auto_approve', condition: collections.abc.Callable | None = None, reason: str = '')
```

A single permission rule for a tool or tool pattern.

## `RateLimitMiddleware`

```python
RateLimitMiddleware(max_calls: int = 50, window_seconds: float = 60.0, scope: str = 'user')
```

Token-bucket rate limiter for agent operations.

Tracks LLM calls per scope key (user_id, tenant_id, or session_id).
When the limit is exceeded within the window, subsequent LLM calls
are blocked and an error is injected.

Args:
    max_calls: Maximum number of LLM calls allowed in the window.
    window_seconds: Time window in seconds.
    scope: What to rate-limit by: "user", "tenant", or "session".

## `ContextCompressionMiddleware`

```python
ContextCompressionMiddleware(config: 'CompressionConfig | None' = None)
```

Applies progressive compression to tool results before each LLM call.

Usage:
    from fg_agents.middleware.context_compression import (
        ContextCompressionMiddleware, CompressionConfig,
    )

    # Default thresholds (10/25/50 message tiers)
    mw = ContextCompressionMiddleware()

    # Custom thresholds for smaller models
    mw = ContextCompressionMiddleware(CompressionConfig(
        fresh_window=5, warm_window=15, cold_window=30,
    ))

    orchestrator = Orchestrator(llm, tools, repo, middleware=[mw])

## `CompressionConfig`

```python
CompressionConfig(fresh_window: 'int' = 10, warm_window: 'int' = 25, cold_window: 'int' = 50, warm_head_chars: 'int' = 2000, warm_tail_chars: 'int' = 500, warm_skip_below: 'int' = 2500, cold_summary_chars: 'int' = 150) -> None
```

Per-agent compression thresholds. Tune based on your model's
context window and typical conversation length.

## `progressive_compress`

```python
progressive_compress(messages: 'list[AgentMessage]', config: 'CompressionConfig | None' = None) -> 'list[AgentMessage]'
```

Apply tiered aging to tool results based on message position.

Returns a NEW list — never mutates input. Idempotent via markers.

Tiers (measured from END of message list):
  - Fresh  (last ``fresh_window``): unchanged
  - Warm   (next ``warm_window``): head + tail truncation
  - Cold   (next ``cold_window``): 1-line stub
  - Expired (beyond ``cold_window``): static placeholder

## `LoopGuardMiddleware`

```python
LoopGuardMiddleware(config: 'LoopGuardConfig | None' = None)
```

Detects and breaks infinite loops in the agent ReAct loop.

Usage::

    from fg_agents.middleware.loop_guard import LoopGuardMiddleware

    engine = AgentEngine(
        llm=llm, tool_registry=registry, repository=repo,
        middleware=[LoopGuardMiddleware()],
    )

With custom config::

    config = LoopGuardConfig(max_identical_calls=5, max_toolonly_turns=12)
    middleware = [LoopGuardMiddleware(config=config)]

## `LoopGuardConfig`

```python
LoopGuardConfig(max_identical_calls: 'int' = 3, max_identical_success_calls: 'int' = 10, max_toolonly_turns: 'int' = 4, max_management_only_turns: 'int' = 5, management_tools: 'frozenset[str]' = frozenset({'manage_plan', 'manage_context', 'manage_skill', 'manage_knowledge', 'manage_objective', 'manage_notes'}), soft_warning_before_hard_stop: 'bool' = True) -> None
```

Configuration for loop detection thresholds.

## `ContextHealthConfig`

```python
ContextHealthConfig(max_tokens: 'int' = 200000, max_messages: 'int' = 100, compress_threshold: 'float' = 0.4, compact_threshold: 'float' = 0.8, warn_threshold: 'float' = 0.85, hard_stop_threshold: 'float' = 0.9) -> None
```

Health thresholds for context window management.

Attach to an AgentDefinition via metadata:
    agent = AgentDefinition(
        ...,
        metadata={"context_health": ContextHealthConfig(max_tokens=200_000)},
    )

Or configure on the engine directly.

## `assess_health`

```python
assess_health(total_input_tokens: 'int', message_count: 'int', config: 'ContextHealthConfig', already_warned: 'bool' = False) -> 'HealthAction'
```

Determine what context management actions should happen this turn.

Called every turn after the LLM response. Actions are NOT mutually
exclusive — multiple can fire in one turn.

Args:
    total_input_tokens: Cumulative input tokens so far
    message_count: Total messages in the session
    config: Health thresholds
    already_warned: Whether warn has already fired (one-shot)

Returns:
    HealthAction with flags for each possible action

## `compute_health_score`

```python
compute_health_score(total_input_tokens: 'int', message_count: 'int', config: 'ContextHealthConfig') -> 'float'
```

Compute context health score from 0.0 (empty) to 1.0 (full).

Token usage is the primary signal (70% weight) because it directly
measures what the API will reject. Message count (30% weight) catches
cases where many small messages accumulate.

## `BaseRepository`

```python
BaseRepository()
```

Abstract base for all persistence backends.

Implementations: PostgresRepository, InMemoryRepository,
SQLiteRepository.

## `create_repository`

```python
create_repository(backend: str = 'memory', **kwargs) -> fg_agents.persistence.base.BaseRepository
```

Factory for persistence backends.

Args:
    backend: One of "memory", "sqlite", "postgres".
    **kwargs: Backend-specific arguments:
        - memory: (no args)
        - sqlite: db_path (str, default "fg_agents.db")
        - postgres: db_url (str), echo (bool)

Returns:
    A BaseRepository instance (call .initialize() before use).

## `InMemoryRepository`

```python
InMemoryRepository()
```

In-memory persistence backend. No database required.

All data lives in Python dicts and is lost on process exit.
Thread-safe for single-event-loop async usage.

## `PostgresRepository`

```python
PostgresRepository(db_url: str, echo: bool = False, pool_size: int = 20, max_overflow: int = 10, pool_recycle: int = 1800)
```

PostgreSQL persistence backend using SQLAlchemy + asyncpg.

All DB operations go through here. No other module touches
SQLAlchemy models directly.

## `SQLiteRepository`

```python
SQLiteRepository(db_path: str = 'fg_agents.db')
```

SQLite persistence backend using aiosqlite.

Usage:
    repo = SQLiteRepository("agents.db")
    await repo.initialize()

## `Repository`

```python
Repository(db_url: str, echo: bool = False, pool_size: int = 20, max_overflow: int = 10, pool_recycle: int = 1800)
```

PostgreSQL persistence backend using SQLAlchemy + asyncpg.

All DB operations go through here. No other module touches
SQLAlchemy models directly.

## `StreamEvent`

```python
StreamEvent(*, id: str = <factory>, type: fg_agents.core.types.EventType, session_id: str, data: dict[str, typing.Any] = <factory>, timestamp: datetime.datetime = <factory>, turn_number: int | None = None) -> None
```

A single event emitted during agent execution.

Events flow: Engine → AsyncIterator → SSE endpoint → Frontend

## `build_system_prompt`

```python
build_system_prompt(agent_def: fg_agents.core.types.AgentDefinition, skills: list[fg_agents.core.types.Skill] | None = None, working_memory_context: str = '', extra_context: str = '', variables: dict[str, typing.Any] | None = None, registered_tools: list | None = None, knowledge_index: list[dict] | None = None, skill_index: list[dict] | None = None, objective: str | None = None, plan: list[dict] | None = None, split_volatile: bool = False) -> str | tuple[str, str]
```

Construct the full system prompt for an agent.

Structure:
    1. Identity   — WHO the agent is (one-liner)
    2. Principles — HOW it operates (modus operandi)
    3. Objective   — WHAT it's working on right now
    4. Skills      — available procedures (name + 1-liner)
    5. Knowledge   — available context (name + 1-liner)
    6. Tools       — available tools (name + 1-liner)
    7. Notes       — session scratch pad
    8. Plan        — active task tracker

Identity and principles come from the agent's system_prompt.
Everything else is assembled here from runtime state.

split_volatile: when True, return (static_prompt, volatile_context) instead
of one string. The static part (sections 1–6) is byte-stable across turns so
provider prompt caches (Together/OpenAI automatic prefix caching, Anthropic
cache_control) keep hitting; the volatile part (Notes + Plan, which change
every turn) is delivered as a trailing message instead of inside the system
prompt, where a change would invalidate the cached prefix of the entire
conversation.

## `load_knowledge`

```python
load_knowledge(sources: list) -> str
```

Load knowledge from multiple source types.

Sources can be:
- str: File path or glob pattern (e.g. "knowledge/*.md")
- dict: Inline knowledge with "title" and "content" keys
- Callable: Sync function that returns a string

Files that don't exist are silently skipped with a warning.

## `AgentScheduler`

```python
AgentScheduler(orchestrator: fg_agents.orchestrator.orchestrator.Orchestrator, repository: fg_agents.persistence.repository.PostgresRepository, agent_definitions: dict[str, fg_agents.core.types.AgentDefinition], poll_interval_seconds: int = 30, pre_execute_hook: typing.Any | None = None, post_execute_hook: typing.Any | None = None)
```

DB-backed agent scheduler.

Runs as a background task, polling the af_schedules table for due jobs.
When a schedule is due, it runs the agent and records the result.

Supports pre/post execution hooks for application-specific logic
(e.g., creating ephemeral tables for incremental data research).

## `ScheduleEntry`

```python
ScheduleEntry(*, id: str = <factory>, name: str, agent_id: str, tenant_id: str | None = None, user_id: str | None = None, schedule_type: str, cron_expression: str | None = None, run_at: datetime.datetime | None = None, event_type: str | None = None, prompt_template: str = '', agent_config: dict[str, typing.Any] = <factory>, variables: dict[str, typing.Any] = <factory>, metadata: dict[str, typing.Any] = <factory>, enabled: bool = True, max_runs: int | None = None) -> None
```

Schedule definition.

## `create_app`

```python
create_app(agents: dict[str, fg_agents.core.types.AgentDefinition], db_url: str | None = None, api_keys: dict[str, str] | None = None, tool_registry: fg_agents.tools.registry.ToolRegistry | None = None, cors_origins: list[str] | None = None, prefix: str = '/api/agent', title: str = 'Fareground Agent API', admin_only: bool = True, **fastapi_kwargs: Any) -> fastapi.applications.FastAPI
```

Create a FastAPI app with the agent framework fully wired.

Args:
    agents: Named agent definitions (e.g., {"assistant": assistant_def}).
    db_url: Database URL. PostgreSQL for production; None defaults to a
        local SQLite file (requires 'fg-agents[sqlite]'); "memory" for
        in-memory persistence.
    api_keys: LLM provider API keys (e.g., {"openai": "sk-..."}).
    tool_registry: Pre-configured ToolRegistry with your tools registered.
    cors_origins: Allowed CORS origins (e.g., ["http://localhost:3000"]).
    prefix: URL prefix for agent endpoints (default "/api/agent").
    title: FastAPI app title.
    admin_only: If True (default), POST /tools and POST /agents return 403.

Returns:
    A configured FastAPI application. Run with: uvicorn module:app

## `create_agent_router`

```python
create_agent_router(orchestrator: fg_agents.orchestrator.orchestrator.Orchestrator, agent_definitions: dict[str, fg_agents.core.types.AgentDefinition] | None = None, service: fg_agents.api.service.AgentService | None = None, admin_only: bool = True, authenticator: collections.abc.Callable[[starlette.requests.Request], collections.abc.Awaitable[fg_agents.api.auth.AuthContext]] | None = None) -> fastapi.routing.APIRouter
```

Create a FastAPI router for the agent framework.

Args:
    orchestrator: The configured Orchestrator instance.
    agent_definitions: Named agent definitions (brain, analyst, etc.).
    service: Optional pre-configured AgentService. If None, one is
             created from orchestrator + agent_definitions.
    admin_only: If True (default), runtime tool/agent registration
                endpoints (POST /tools, POST /agents) return 403.
                Set False to enable runtime registration.
    authenticator: Resolves each request to a verified AuthContext. Every
                route is gated by it, and a session/memory is only
                reachable by its own tenant. When omitted, an
                UnauthenticatedAccess default keeps single-tenant/local
                deployments working but logs a loud warning — configure a
                real authenticator before exposing this multi-tenant.

Returns:
    APIRouter to mount on your FastAPI app.

## `AgentService`

```python
AgentService(orchestrator: fg_agents.orchestrator.orchestrator.Orchestrator, agent_definitions: dict[str, fg_agents.core.types.AgentDefinition] | None = None)
```

Stateless service layer for agent operations.

Delegates to Orchestrator and Repository via their public APIs.
No HTTP, no framework — pure business logic.

## `get_service`

```python
get_service(request: starlette.requests.Request) -> fg_agents.api.service.AgentService
```

FastAPI dependency: inject the AgentService singleton.

The service is stored on app.state by create_app() or manually.

## `get_user_context`

```python
get_user_context(request: starlette.requests.Request) -> fg_agents.core.types.UserContext
```

FastAPI dependency: extract user/tenant context from request headers.

Reads these headers (your app sets them via auth middleware):
- X-User-ID
- X-Tenant-ID
- X-Org-ID

Override this dependency to use JWT claims, session cookies, etc.

## `AgentFrameworkError`

Base exception for all framework errors.

## `LLMError`

```python
LLMError(message: str, provider: str = '', model: str = '', status_code: int = 0, retryable: bool = False)
```

Error during LLM call.

## `LLMRateLimitError`

```python
LLMRateLimitError(message: str, retry_after_seconds: float = 0, **kwargs)
```

Rate limit exceeded — retryable.

## `ContextOverflowError`

```python
ContextOverflowError(message: str, tokens_used: int = 0, token_limit: int = 0, **kwargs)
```

Context window exceeded.

## `ToolExecutionError`

```python
ToolExecutionError(message: str, tool_name: str = '', tool_call_id: str = '', original_error: Exception | None = None)
```

Error during tool execution.

## `ToolNotFoundError`

```python
ToolNotFoundError(message: str, tool_name: str = '', tool_call_id: str = '', original_error: Exception | None = None)
```

Requested tool does not exist in registry.

## `ToolDeniedError`

```python
ToolDeniedError(message: str, tool_name: str = '', tool_call_id: str = '', original_error: Exception | None = None)
```

Tool execution was denied by permission middleware.

## `ToolTimeoutError`

```python
ToolTimeoutError(message: str, tool_name: str = '', tool_call_id: str = '', original_error: Exception | None = None)
```

Tool execution timed out.

## `SessionError`

Error related to session management.

## `SessionNotFoundError`

Session does not exist.

## `MaxTurnsExceededError`

```python
MaxTurnsExceededError(session_id: str, turns: int, max_turns: int)
```

Agent reached max_turns without completing.

## `SubAgentError`

```python
SubAgentError(message: str, child_session_id: str = '', original_error: Exception | None = None)
```

Error in a sub-agent execution.

## `MiddlewareError`

```python
MiddlewareError(message: str, middleware_name: str = '')
```

Error in middleware processing.

## `SkillNotFoundError`

Requested skill does not exist.

