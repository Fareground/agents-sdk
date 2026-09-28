"""An OpenAI-compatible stream reports a tool call's arguments as they arrive, as the Anthropic stream does."""

import asyncio
from types import SimpleNamespace

from fg_agents.core.llm import AgentLLM


def _delta(tool_calls):
    return SimpleNamespace(content=None, tool_calls=tool_calls, reasoning_content=None, reasoning=None)


def _tc_delta(index, tid=None, name=None, args=None):
    return SimpleNamespace(index=index, id=tid, function=SimpleNamespace(name=name, arguments=args))


def _chunk(delta=None, finish_reason=None):
    return SimpleNamespace(choices=[SimpleNamespace(delta=delta or _delta(None), finish_reason=finish_reason)],
                           usage=None)


class _FakeClient:
    def __init__(self, chunks):
        async def create(**kwargs):
            async def stream():
                for chunk in chunks:
                    yield chunk
            return stream()
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))


def test_stream_openai_reports_tool_arguments_while_they_are_written():
    chunks = [
        _chunk(_delta(tool_calls=[_tc_delta(0, tid="call_a", name="draft", args='{"contract": {"na')])),
        _chunk(_delta(tool_calls=[_tc_delta(0, args='me": "Bakery"}}')])),
        _chunk(finish_reason="tool_calls"),
    ]
    llm = AgentLLM()

    async def _run():
        async def _fake_get_client(provider):
            return _FakeClient(chunks)
        llm._get_client = _fake_get_client  # type: ignore[assignment]
        return [c async for c in llm._stream_openai([], None, "gpt-oss", "", 0.0, 256, "cerebras")]

    events = asyncio.run(_run())
    deltas = [e for e in events if e.type == "tool_call_delta"]
    assert [(e.tool_call_id, e.tool_name) for e in deltas] == [("call_a", "draft")] * 2
    assert "".join(e.arguments_delta for e in deltas) == '{"contract": {"name": "Bakery"}}'
    [end] = [e for e in events if e.type == "tool_call_end"]
    assert end.tool_call.arguments == {"contract": {"name": "Bakery"}}
    assert events.index(deltas[-1]) < events.index(end)
