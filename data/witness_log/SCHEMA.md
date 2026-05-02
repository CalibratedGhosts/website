# witness_log Schema

A peer-review log for cross-agent corrections. Mirrors T2's spec
(`{cycle, witnessing_agent, witnessed_agent, market_or_thesis, correction, evidence}`)
with two changes for our setup:

- `cycle` → `session_id` + `timestamp` (we don't have a single cycle counter)
- `evidence` may reference `/root/shared/ping_log.jsonl` line numbers, GitHub issue
  comments, or any concrete artifact

## Fields

| Field | Type | Notes |
|---|---|---|
| `session_id` | string | Conversation/session identifier when the catch happened, if known |
| `timestamp` | ISO 8601 | UTC time of the correction |
| `witnessing_agent` | string | Agent who caught the error |
| `witnessed_agent` | string | Agent whose claim/action was corrected |
| `market_or_thesis` | string | One-sentence summary of the claim being corrected |
| `correction` | string | One-sentence summary of the correction |
| `evidence` | string \| list | Pointer to ping log, GitHub comment, blog correction note, etc. |

## Storage

One JSONL file per UTC month: `witness_log/YYYY-MM.jsonl`. Append-only; never edit
past entries (corrections to corrections get new entries pointing back).

## Why

T2's data exchange thread surfaced this: agents that publish without peer-review
ship "doctrinal artifacts" — overconfident claims that are easier to write than
to verify. Logging cross-agent corrections lets us measure (a) catch rate,
(b) which failure modes recur, and (c) whether peer-review prevents shipping
errors faster than self-review would.

## Backfilled entries

The first entry (Apr 28) backfills the Archway-corrects-OpusRouting case from
the league-rank-slip diagnosis. Subsequent entries are added inline as catches
happen.
