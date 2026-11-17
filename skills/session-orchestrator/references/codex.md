# Codex integration

Discover the interfaces in the current installation. Tool names below describe the original exercise, not a guarantee for every release.

## Sessions and projects

- `list_projects` resolves destination IDs. `list_threads` finds workers and their sidebar project membership.
- `read_thread` reads original requests, direct user interventions, and results. Follow page cursors for older relevant messages. A listing summary is not a message review.
- `create_thread` creates persistent workers in selected projects. Default to local execution; use a worktree or other environment only when requested and supported. Preserve model defaults unless overrides are authorized.
- `fork_thread` retains history but is not the default way to continue another chat in the current coordinator.
- `wait_threads` provides compact status and reusable cursors. A completed turn does not imply a completed task.
- `send_message_to_thread` sends follow-up input under its authorization rules. Verify whether the current host queues or steers it rather than assuming queue semantics.

Project creation is host-dependent. If no supported registration tool exists, create authorized independent filesystem roots and use them as session working directories through the supported CLI or host interface. Do not call them registered sidebar projects unless that is verified. Never edit internal app databases or settings files to simulate registration. Reuse an existing chat/work project pair only when that matches the user's request.

Keep returned session IDs, actual working directories, and app project membership distinct. An independent app-server process may report different runtime status or project metadata from Desktop. Use Desktop's list for sidebar membership and actual message history for consumption.

## Native queues

Inspect the installed public interface first:

```sh
codex --version
codex queue --help
codex app-server --help
```

Queue into an existing session with:

```sh
codex queue --thread THREAD_ID --message 'Complete task or correction'
```

This does not create a separate CLI conversation. A Desktop-visible session retains the same thread ID. Verify delivery through its message history. The UI's pending-list display requires UI observation if that is the claim under test. Some versions provide `--resume`; inspect local help and do not resend merely to wake a session.

Prefer native MCP queue tools when exposed. Otherwise [scripts/codex_queue.py](../scripts/codex_queue.py) sends one request to the installed `codex app-server --stdio` using its public initialization handshake. It prints the unmodified JSON-RPC response, creates no sessions, stores no ledger, and runs no service.

The queue protocol was exercised with Codex `0.169.0-alpha.11.1` and is experimental. If methods or parameters are rejected, retain the error and inspect that version's schema with `codex app-server generate-json-schema --help`. Do not silently substitute steer or touch internal databases.

Run from the installed skill directory, passing a JSON object on stdin:

```sh
python3 scripts/codex_queue.py list <<'JSON'
{"threadId":"THREAD_ID"}
JSON
```

| Operation | Parameters besides `threadId` |
| --- | --- |
| `list` | Pagination fields supported by the installed schema; inspect `nextCursor`. |
| `add` | `clientUserMessageId`, `input` |
| `update` | `queuedSubmissionId`, replacement `input` |
| `delete` | `queuedSubmissionId` |
| `reorder` | `queuedSubmissionIds`, the complete pending order |

An add request has this shape:

```json
{
  "threadId": "THREAD_ID",
  "clientUserMessageId": "CLIENT_MESSAGE_UUID",
  "input": [{"type": "text", "text": "Complete assignment"}]
}
```

Use a fresh UUID for new input and retain it for an uncertain retry. Mutation responses return the actual `queuedSubmission.id`. Do not confuse it with a completed turn's message ID. Re-read before reordering because consumption may change the queue between requests. Never remove unfamiliar work merely to make an experimental order succeed.

## Observable verification

When the user requests a queue exercise, use authorized isolated work and harmless distinguishable inputs. Keep a worker busy briefly, add several items, edit one, delete one, and reorder survivors. Verify native read-back and later consumed messages or artifacts: edited content is used, deleted or superseded input does not execute, order matches, and no pending input remains. Do not introduce synthetic tasks into unrelated work just to exercise the skill.

For two-project verification, check distinct roots, actual session working directories, exclusive artifact paths, and the absence of worker output in the chat project. Include a direct user correction when the requested workflow depends on it. Report separately whether the host registered both roots in the sidebar.

This skill supplies instructions and a thin client, not a backend, credentials, or guaranteed models. If the host lacks an operation, describe the missing capability and use only an authorized supported route. Do not bypass a computer-use restriction through another UI-control path.
