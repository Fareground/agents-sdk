"""Regression: spurious inline <think> must not swallow the answer when the
model reasons on the dedicated channel.

Qwen3.7-Plus on Together streams its chain-of-thought via delta.reasoning AND
prefixes the content channel with an unclosed "<think>\n" (chat-template
artifact). The old parser fed content through the _ThinkSplitter, entered
think-mode on the orphan tag, and routed the entire visible answer into the
thinking channel — the stored assistant message had no text. When the
reasoning channel is active, literal think tags in content are stripped and
content streams as text.
"""

import asyncio
from types import SimpleNamespace

from fg_agents.core.llm import AgentLLM


def _delta(content=None, reasoning=None):
    return SimpleNamespace(content=content, tool_calls=None,
                           reasoning_content=None, reasoning=reasoning)


def _chunk(delta=None, finish_reason=None, usage=None):
    choices = [] if delta is None and finish_reason is None else [
        SimpleNamespace(delta=delta or _delta(), finish_reason=finish_reason)
    ]
    return SimpleNamespace(choices=choices, usage=usage)


class _FakeStream:
    def __init__(self, chunks):
        self._chunks = chunks

    def __aiter__(self):
        async def gen():
            for c in self._chunks:
                yield c
        return gen()


class _FakeCompletions:
    def __init__(self, chunks):
        self._chunks = chunks

    async def create(self, **kwargs):
        return _FakeStream(self._chunks)


class _FakeClient:
    def __init__(self, chunks):
        self.chat = SimpleNamespace(completions=_FakeCompletions(chunks))


def _run_stream(chunks):
    llm = AgentLLM()

    async def _run():
        async def _fake_get_client(provider):
            return _FakeClient(chunks)
        llm._get_client = _fake_get_client  # type: ignore[assignment]
        out = []
        async for c in llm._stream_openai([], None, "Qwen/Qwen3.7-Plus", "", 0.0, 256, "together"):
            out.append(c)
        return out

    return asyncio.run(_run())


def test_reasoning_channel_strips_spurious_think_tag():
    chunks = [
        _chunk(_delta(reasoning="Thinking Process:\n1. Identify the question.")),
        _chunk(_delta(content="<think>\n")),
        _chunk(_delta(content="2 + 2 equals 4.")),
        _chunk(finish_reason="stop"),
    ]
    out = _run_stream(chunks)
    text = "".join(c.text or "" for c in out if c.type == "text_delta")
    thinking = "".join(c.text or "" for c in out if c.type == "thinking_delta")
    assert text == "\n2 + 2 equals 4."
    assert "<think>" not in text
    assert "Thinking Process" in thinking
    assert "equals 4" not in thinking


def test_inline_think_splitter_still_works_without_reasoning_channel():
    # gpt-oss style: no reasoning channel, real inline <think>...</think>.
    chunks = [
        _chunk(_delta(content="<think>plan the answer</think>")),
        _chunk(_delta(content="The answer is 4.")),
        _chunk(finish_reason="stop"),
    ]
    out = _run_stream(chunks)
    text = "".join(c.text or "" for c in out if c.type == "text_delta")
    thinking = "".join(c.text or "" for c in out if c.type == "thinking_delta")
    assert text == "The answer is 4."
    assert thinking == "plan the answer"


def test_openrouter_continuation_survives_tool_roundtrip_without_visible_leak():
    """Provider continuation blocks must accompany the original tool call."""
    from fg_agents.core.types import AgentDefinition, EventType, SessionStatus
    from fg_agents.tools.decorators import tool
    from tests.test_engine import build_engine

    details = [
        {'type': 'reasoning.text', 'text': 'Planning ', 'index': 0,
         'id': 'reason-1', 'format': 'anthropic-claude-v1'},
        {'type': 'reasoning.text', 'text': 'continued', 'signature': 'opaque-signature',
         'index': 0, 'id': 'reason-1', 'format': 'anthropic-claude-v1'},
        {'type': 'reasoning.encrypted', 'data': 'opaque-encrypted', 'index': 1},
    ]
    requests = []

    @tool(name='lookup', description='Read data')
    async def lookup() -> str:
        return 'found'

    class Client:
        def __init__(self):
            self.chat = SimpleNamespace(completions=self)

        async def create(self, **kwargs):
            requests.append(kwargs)
            if len(requests) == 1:
                chunks = []
                for detail in details:
                    delta = _delta()
                    delta.reasoning_details = [detail]
                    chunks.append(_chunk(delta))
                delta = _delta()
                delta.tool_calls = [SimpleNamespace(index=0, id='call-1',
                    function=SimpleNamespace(name='lookup', arguments='{}'))]
                return _FakeStream([*chunks, _chunk(delta), _chunk(finish_reason='tool_calls')])
            return _FakeStream([_chunk(_delta(content='Done')), _chunk(finish_reason='stop')])

    async def run():
        llm = AgentLLM()
        client = Client()
        async def get_client(provider):
            return client
        llm._get_client = get_client
        engine, repo, _ = await build_engine(llm, tools=[lookup])
        agent = AgentDefinition(name='continuation', model='openrouter:anthropic/claude-test',
                                max_llm_retries=0, tools=['lookup'])
        events = [event async for event in engine.run('continuation', 'Use lookup', agent)]
        assert (await repo.get_session('continuation')).status == SessionStatus.COMPLETED
        assert len(requests) == 2
        assistant = next(m for m in requests[1]['messages'] if m['role'] == 'assistant')
        assert assistant.get('reasoning_details') == details
        assert assistant['tool_calls'][0]['id'] == 'call-1'
        assert 'reasoning' not in assistant  # No duplicate plaintext fallback.
        visible = [e for e in events if e.type in (EventType.LLM_TEXT_DELTA, EventType.LLM_THINKING)]
        assert all('opaque-' not in e.model_dump_json() for e in visible)
        # State survives the same JSON content encoding used by durable repositories.
        from fg_agents.core.llm import _messages_to_openai
        from fg_agents.core.types import AgentMessage
        saved = [AgentMessage.model_validate_json(m.model_dump_json())
                 for m in await repo.get_messages('continuation')]
        replay = _messages_to_openai(saved, '', provider='openrouter', model_name='anthropic/claude-test')
        assert next(m for m in replay if m['role']=='assistant')['reasoning_details'] == details
        for provider, model in [('openai', 'anthropic/claude-test'), ('openrouter', 'different')]:
            other = _messages_to_openai(saved, '', provider=provider, model_name=model)
            assert not any('reasoning_details' in m for m in other)

    asyncio.run(run())


def test_openrouter_plain_reasoning_fallback_and_complete_result():
    details = {'type': 'reasoning.encrypted', 'data': 'opaque', 'signature': None}

    async def run(provider, with_details):
        llm = AgentLLM()
        delta = _delta(reasoning='one')
        if with_details:
            delta.reasoning_details = [details]
        client = _FakeClient([_chunk(delta), _chunk(_delta(reasoning=' two')),
                              _chunk(_delta(content='answer')), _chunk(finish_reason='stop')])
        async def get_client(provider):
            return client
        llm._get_client = get_client
        return await llm._complete_openai([], None, 'model', '', 0.0, 256, provider)

    plain = asyncio.run(run('openrouter', False))
    assert plain.content == 'answer'
    assert plain.provider_state == {'provider': 'openrouter', 'model': 'model', 'reasoning': 'one two'}
    opaque = asyncio.run(run('openrouter', True))
    assert opaque.provider_state['reasoning_details'] == [details]
    assert 'reasoning' not in opaque.provider_state
    assert asyncio.run(run('together', True)).provider_state is None
