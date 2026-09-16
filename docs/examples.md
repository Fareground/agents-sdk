# Examples

Start with [the quickstart](getting-started.md) for a complete tool-using conversation.

The repository's [examples directory](https://github.com/Fareground/agents-sdk/tree/main/examples) includes a facade hello-world, tools, persistence, a web application and frontend SSE clients. Install the extras required by the example and configure its selected provider.

## Clone and install

```bash
git clone https://github.com/Fareground/agents-sdk.git
cd agents-sdk
python -m pip install -e ".[anthropic,web,sqlite]"
```

## Suggested progression

1. Run one prompt and inspect `AgentRunResult`.
2. Add one read-only business tool and inspect its generated schema.
3. Continue a conversation with the same session.
4. Persist it to SQLite and verify it survives a restart.
5. Stream events to your UI.
6. Add authentication and the application's production boundaries before exposing it.

For an environment-building agent, give it access to the Environments SDK's guide, checker and controlled execution tools. Require scenario-level tests and inspect the generated contract before running it for a customer.
