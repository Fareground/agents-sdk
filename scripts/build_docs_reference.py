"""Generate reference pages from the public exports of the current source."""
import inspect
import re
from pathlib import Path

import fg_agents

root = Path(__file__).resolve().parents[1]
lines = ["# Public API reference", "", "Generated from public exports in `fg_agents`. See [API guide](api.md) for common workflows.", ""]
for name in fg_agents.__all__:
    obj = getattr(fg_agents, name)
    if not (inspect.isfunction(obj) or inspect.isclass(obj)):
        continue
    lines += [f"## `{name}`", ""]
    try:
        signature = re.sub(r" at 0x[0-9a-f]+", "", str(inspect.signature(obj)))
        lines += ["```python", f"{name}{signature}", "```", ""]
    except (ValueError, TypeError):
        pass
    if inspect.getdoc(obj):
        lines += [inspect.getdoc(obj), ""]
(root / "docs/reference.md").write_text("\n".join(lines) + "\n")
print("Generated public API reference")
