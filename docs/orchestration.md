# Skills and orchestration

## Skills are reusable instructions

A skill pairs a prompt template with required tool names. It helps an agent follow a procedure; it does not grant authorization or install a tool implementation.

```python
from fg_agents import SkillsManager

skills = SkillsManager()
skills.register(SkillsManager.from_markdown(
    skill_id="inventory_review",
    name="Inventory review",
    markdown_content="""# Inventory review
Check current stock before making a recommendation.
State the lead-time assumption and show the reorder calculation.
""",
    required_tools=["stock"],
))
```

Pass the manager to `AgentEngine` or `Orchestrator`, register the required tools, and include the skill ID in the agent definition's `skills` list. Missing skills are logged during resolution; validate your configured skill IDs before deploying.

## When to use an orchestrator

Use `Orchestrator` when a coordinator must delegate work to specialist agents. It wraps the engine, manages sub-agents, and wires delegation tools. For a single assistant, `Agent` is simpler.

An orchestrator can register built-in tools automatically. Review the resulting registry and expose a deliberate tool list in each definition. Set `auto_register_builtins=False` when you need to supply that registry yourself.

## Lifecycle

Construct the LLM client, tool registry and repository; create the orchestrator; call `await orchestrator.initialize()`; consume its run events; and call `await orchestrator.shutdown()` when the application stops.

Sub-agent definitions can specify deadlines and the parent can limit parallel agents. Bound each delegated task and inspect partial results if a deadline expires. More agents do not guarantee a better answer; measure whether delegation improves your specific workflow.

See [API reference](api.md), the [generated public reference](reference.md), and the repository's [examples](examples.md).
