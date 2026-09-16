# Web integration

## A local service

Install the web extra and a model provider:

```bash
python -m pip install "fg-agents[web,anthropic]"
```

Save as `app.py`:

```python
import os
from fg_agents import AgentDefinition, create_app

assistant = AgentDefinition(
    name="assistant",
    model=os.environ["AGENT_MODEL"],
    system_prompt="Help the user reason about inventory decisions.",
    tools=[],
    max_turns=6,
)
app = create_app(agents={"assistant": assistant}, db_url="memory")
```

```bash
uvicorn app:app --host 127.0.0.1
```

This is a local, ephemeral demonstration. `db_url="memory"` avoids a database dependency. Omitting `db_url` selects a local SQLite file and requires the `sqlite` extra.

## HTTP and streaming

The default prefix is `/api/agent`. Create a session with `POST /sessions`, then send messages to `POST /sessions/{id}/messages`; responses stream as Server-Sent Events. The generated FastAPI OpenAPI schema documents request bodies for the configured application.

Read [streaming](streaming.md) before writing a frontend parser. A network chunk is not necessarily a complete SSE event. Handle reconnects and errors deliberately.

## Authentication for an exposed service

The default router uses unauthenticated, shared-tenant access. `admin_only=True` restricts certain registration endpoints; it is not a replacement for request authentication.

For an exposed or multi-tenant application, mount `create_agent_router(..., authenticator=...)` in your own FastAPI app. An authenticator validates a request and returns `AuthContext` from `fg_agents.api.auth`, or raises HTTP 401. Derive the tenant from verified credentials, not a user-supplied request body.

`HeaderAuthenticator` is for a trusted proxy that strips incoming identity headers and sets verified ones. It is not safe to trust those headers from arbitrary clients.

## Application lifecycle

Initialize persistence before handling requests and close it during shutdown. Configure CORS for the actual frontend origins, enforce request limits, and ensure session access follows your tenant boundary. See [production integration](production.md) and [persistence](persistence.md).
