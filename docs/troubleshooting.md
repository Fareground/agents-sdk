# Troubleshooting

| Symptom | First check |
|---|---|
| `ModelDetectionError` | Configure a provider or pass `model=` explicitly |
| Provider import error | Install the relevant provider extra |
| SQLite import error | Install `fg-agents[sqlite]` or choose `memory` |
| Tool never called | Definition's tool names, registered schema and prompt |
| Tool rejected before execution | Malformed or truncated arguments; inspect the tool event |
| Conversation disappears | In-memory storage or a different session ID |
| Streaming stops without final text | Error events and exceptions from the iterator |
| Duplicate external action | Retry behavior and application idempotency |
| Unauthorized shared access | Default authenticator; configure the HTTP trust boundary |
| Missing skill | Registered IDs and the definition's `skills` list |

## Capture a useful failure

`AgentRunError` carries the session ID and partial events. Keep the original cause where available. Record the installed version, provider, configured model and a minimal tool schema. Remove credentials and private user data before sharing a reproduction.

## Close streams

If you stop reading early, explicitly close the async generator with `contextlib.aclosing`. Otherwise cleanup may wait for garbage collection. See [streaming](streaming.md).

## Inspect the actual public surface

Use [API reference](api.md) for the common interfaces and [generated reference](reference.md) for exported symbols. Do not infer an implemented feature from a roadmap ticket or an old example.
