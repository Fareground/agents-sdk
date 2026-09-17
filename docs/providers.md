# Models and providers

## Explicit model selection

Use a provider-qualified name: `anthropic:<model-id>`, `openai:<model-id>`, `google:<model-id>` or `ollama:<model-id>`. Choose the model available in your deployment and pass it explicitly for reproducible configuration.

```python
import os
from fg_agents import Agent

agent = Agent(model=os.environ["AGENT_MODEL"])
```

Model availability and capabilities belong to the provider. A provider-qualified identifier does not guarantee that every model supports every tool or streaming feature.

## Installation and credentials

| Provider | Extra | Credentials |
|---|---|---|
| Anthropic | `fg-agents[anthropic]` | `ANTHROPIC_API_KEY` |
| OpenAI | `fg-agents[openai]` | `OPENAI_API_KEY` |
| Google | `fg-agents[google]` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| Local Ollama | OpenAI-compatible client path | Local service and an installed model |

`AgentLLM` accepts an `api_keys` mapping for host-managed credentials and a `custom_providers` mapping for compatible base URLs. Keep keys out of agent prompts and persisted user-visible context.

For OpenRouter, configure its base URL explicitly and use the `openrouter`
provider name:

```python
from fg_agents.core.llm import AgentLLM

llm = AgentLLM(custom_providers={"openrouter": "https://openrouter.ai/api/v1"})
agent = Agent(model="openrouter:" + os.environ["OPENROUTER_MODEL"], llm=llm)
```

Set `OPENROUTER_API_KEY`. From 0.4.6, the engine preserves provider continuation
metadata across tool calls and persistence. It replays that metadata only when
calling the same provider and model; opaque signatures and encrypted blocks do
not become visible assistant text. Lower-level completion callers receive this
state in `LLMResponse.provider_state`. When managing history yourself, preserve
it as an assistant content block alongside the original text and tool calls:

```python
from fg_agents import AgentMessage, MessageRole

content = [{"type": "text", "text": response.content}]
if response.provider_state:
    content.append({"type": "provider_state", "state": response.provider_state})
message = AgentMessage(role=MessageRole.ASSISTANT, content=content,
                       tool_calls=response.tool_calls)
```

The engine handles this automatically.

## Automatic detection

When the facade's model is omitted, detection checks configured Anthropic, OpenAI and Google credentials, then probes local Ollama. If nothing is usable it raises `ModelDetectionError`. [API reference](api.md#model-auto-detection) lists the exact defaults for this release.

Automatic detection is convenient locally. Explicit model configuration avoids a different installed credential changing your deployed model unexpectedly.

## Limits and failures

`AgentDefinition` includes `max_turns`, `max_tokens_per_turn`, `llm_timeout_seconds`, `max_llm_retries` and `fallback_models`. Configure them for the task. A per-response token cap is not a total account spending limit.

Review fallback and retry behavior against your workload before enabling it. If a request's outcome is uncertain, reconcile externally visible work before retrying it. See [production integration](production.md).
