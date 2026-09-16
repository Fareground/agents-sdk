# Tools and middleware

## Define a focused tool

```python
from fg_agents import tool

@tool(description="Calculate a reorder quantity from a target and available stock.")
def reorder_quantity(target: int, available: int) -> dict:
    if target < 0 or available < 0:
        return {"error": "target and available must be non-negative"}
    return {"quantity": max(0, target - available)}
```

Simple type hints create parameter schemas. Descriptions should tell the model when to use the tool, which units it expects, and what it returns. Validate business constraints inside the handler.

## Explicit schemas

Use `json_schema=` when you need nested shapes, enums or constraints beyond the simple annotation inference. The decorator exposes that schema to the model; do not assume a model provider enforces every constraint. Handler validation remains necessary.

```python
from fg_agents import tool

@tool(
    description="Look up a supported product category.",
    json_schema={
        "type": "object",
        "properties": {"category": {"type": "string", "enum": ["coffee", "tea"]}},
        "required": ["category"],
        "additionalProperties": False,
    },
)
def category_info(category: str) -> dict:
    if category not in {"coffee", "tea"}:
        raise ValueError("Unsupported category")
    return {"category": category}
```

## Register and expose

Pass functions to `Agent(tools=[...])`, or register them in a `ToolRegistry` for the engine. A definition's `tools` list selects which registered names are available. Keep that list explicit for each role.

Sync functions run in a thread; async functions run natively. A correctly typed `ExecutionContext` parameter named `ctx` or `context` is injected by the framework and hidden from the model's argument schema.

## Failure behavior

Use concise structured errors that tell the model what to fix. The engine rejects incomplete or malformed model tool arguments instead of executing the handler with invented defaults. Timeouts, permission denials and execution failures are distinct tool outcomes; inspect events for the cause.

Retries are appropriate only where repeating an operation is safe. For a real order or payment, use a stable idempotency key and verify the external result after an uncertain timeout.

## Middleware

`AgentEngine(middleware=[...])` accepts hooks before and after model calls, before and after tool calls, on turn completion and on error. Middleware runs in registration order. Returning `None` from `before_tool_call` blocks a call.

Shipped middleware covers audit, token tracking, permissions, rate limits, loop guarding and context compression. [API reference](api.md#middleware) gives hook signatures. Instantiate only what the task needs and test blocked as well as successful tool calls.
