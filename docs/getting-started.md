# Run your first agent

## 1. Install a provider

```bash
python -m pip install "fg-agents[anthropic]"
```

Configure `ANTHROPIC_API_KEY` through your environment or secret manager. Set `AGENT_MODEL` to the provider-qualified model you want to use, such as `anthropic:<model-id>`. Use a model available to your account.

For OpenAI use the `openai` extra and `OPENAI_API_KEY`; for Google use the `google` extra and `GOOGLE_API_KEY` or `GEMINI_API_KEY`. See [providers](providers.md).

## 2. Ask a question

Save as `hello.py`:

```python
import asyncio
import os
from fg_agents import ask

async def main():
    result = await ask(
        "Give me three questions to ask before changing an inventory policy.",
        model=os.environ["AGENT_MODEL"],
    )
    print(result.text)

asyncio.run(main())
```

```bash
python hello.py
```

`ask` creates and closes an ephemeral agent. It returns an `AgentRunResult`, whose `text` is the answer and `events` contains the run's events. Model responses vary; there is no fixed expected answer.

## 3. Add a tool and conversation

```python
import asyncio
import os
from fg_agents import Agent, tool

@tool(description="Return the current on-hand inventory for a known SKU.")
def stock(sku: str) -> dict:
    inventory = {"coffee": 42, "tea": 18}
    if sku not in inventory:
        return {"error": "Unknown SKU", "known_skus": list(inventory)}
    return {"sku": sku, "on_hand": inventory[sku]}

async def main():
    async with Agent(
        model=os.environ["AGENT_MODEL"],
        tools=[stock],
        system_prompt="Use stock to check inventory. Do not invent inventory counts.",
        max_turns=6,
    ) as agent:
        result = await agent.run("How much coffee do we have?")
        print(result.text)
        follow_up = await agent.run("And tea?")
        print(follow_up.text)

asyncio.run(main())
```

Both messages use the same conversation. The context manager closes the repository when finished. The default repository is in memory; use [persistence](persistence.md) to keep conversations across restarts.

## 4. Handle failures

```python
from fg_agents import AgentRunError

try:
    result = await agent.run("Check coffee inventory")
except AgentRunError as error:
    print(error.session_id)
    print(error.events)  # partial events, useful for diagnosis
```

This fragment belongs inside an async function while `agent` is open. `run()` presents a uniform error contract. Streaming callers must handle both error events and iterator exceptions.

## Next steps

[Understand the execution model](concepts.md), [build tools](tools.md), or [stream to an application](streaming.md).
