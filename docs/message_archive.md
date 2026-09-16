# Recovering archived messages

Authorize the session owner and tenant before calling repository methods.

`await repository.get_message(session_id, message_id)` returns one original
message, including summarized messages and assistant tool arguments, or `None`.
It cannot retrieve an ID from another session. SQLite and PostgreSQL use a
targeted query; the in-memory backend avoids copying unrelated messages.

`repository.iter_messages(session_id, batch_size=64)` scans archived originals
in bounded batches. `include_summarized=False` excludes summarized originals.
The batch size must be an integer from 1 to 256. Durable repositories use a
created-at/ID keyset and a high-water boundary, not growing SQL offsets. They
release the query cursor/connection before yielding messages. The high-water
boundary excludes newly appended, later messages; it is not a transactional
snapshot against concurrent deletion or backdated insertion.

Use this iterator for archive search/recovery, not for building live model
context: tie ordering is deterministic by ID in durable repositories and is
not a new guarantee of assistant/tool execution order. `get_messages()` and
live context ordering are unchanged. No originals are deleted or shortened.

Bounded hydration does not make a full-content search constant-time. Consumers
should retain only their requested result page. A single very large original
still needs memory proportional to that original. Third-party repositories
inherit compatible all-row fallbacks until they implement the efficient reads.

Run PostgreSQL acceptance against a disposable database using
`SDK_TEST_DATABASE_URL`, then `python -m pytest tests/test_archive_reads.py`.

## Bounded active context

`await repository.get_context_windows(session_id, head_chars=12000,
tail_chars=400, exempt_tools=())` returns active messages in the same order as
`get_messages()`. Each item has `message`, `partial`, `head`, `tail` and
`total_characters`. A partial item has an empty `message.content`; explicitly
label the head and tail as an excerpt before including them in model context.
Use `get_message(session_id, message.id)` to recover its complete original.

Only large plain-text tool results are projected. User instructions, assistant
messages, tool arguments, structured content and named `exempt_tools` remain
whole. The head must be an integer from 1 to 64000, and the tail must be an
integer from zero to the head size. Booleans are not accepted as sizes.

SQLite and PostgreSQL keep an additive, derived cache of content windows and
backfill it lazily for old messages. Original messages remain unchanged. The
cache is removed with its session history and can be rebuilt from originals.
Memory and third-party fallback repositories provide the same return shape,
but already hydrate complete messages and do not promise bounded storage I/O.
