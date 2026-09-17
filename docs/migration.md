# Names, versions and migration

| Surface | Name |
|---|---|
| Product | Agents SDK |
| GitHub repository | `Fareground/agents-sdk` |
| Python distribution | `fg-agents` |
| Python import | `fg_agents` |

The public rename does not change installation commands or imports. Earlier repository URLs included `agent-framework` and `agent-sdk`. Update your remote:

```bash
git remote set-url origin https://github.com/Fareground/agents-sdk.git
```

These pages document version 0.4.6. Pin deployed dependencies, read the [changelog](https://github.com/Fareground/agents-sdk/blob/main/CHANGELOG.md), and run provider, tool and persistence acceptance checks before upgrading.

Existing compatibility identifiers such as `AgentFrameworkError` remain unchanged. Renaming an exception or import solely to match product branding would be a separate breaking change.
