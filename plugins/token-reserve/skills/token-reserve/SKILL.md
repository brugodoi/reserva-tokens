---
name: token-reserve
description: Token spending control with a mandatory reserve of the plan limit for emergencies. Use when the user asks about token consumption/usage/limits, when the "[TOKEN RESERVE MODE]" warning appears, before large tasks (broad refactors, sweeping many files, multiple subagents, extensive research), or when the user asks to save tokens.
---

# Token reserve

The user must ALWAYS keep part of the plan limit (5-hour window and weekly limit)
free for urgent situations.

## Configuration and current usage
- `~/.claude/token-reserve/config.json`: `reserve` (% to keep free, default 20), `warning`
  (alert margin before the limit, default 15) and `urgent` (list of what may use the reserve).
- `~/.claude/token-reserve/usage.json`: last known usage (`used` = % consumed, `resets_at` = reset epoch).
- The status line shows `5h NN%` and `7d NN%` (yellow in the warning band, red in the reserve).
- The user can run `/usage` for the official details.
- If the files are missing or stale, say so and suggest `/usage` or
  `/token-reserve:setup` — never make up numbers.

## Operating bands (example with reserve 20 and warning 15)

| Usage (higher of 5h and 7d) | Mode | Behavior |
|---|---|---|
| < 65% | Normal | Work normally, but without waste. |
| 65–79% | Warning | Economy mode (below). Before a large task, estimate the cost and tell the user. |
| ≥ 80% | **Reserve** | Only the configured urgent cases without asking. Anything else: report current usage and when it resets, and ask for explicit confirmation before proceeding. |

Even in the reserve, work in economy mode and focus on resolving the emergency first.

## Economy mode
- Don't launch subagents or extensive web research unless the user asks.
- Read parts of files (offset/limit, grep) instead of whole files; for logs use `tail`/filters.
- Don't re-read files already seen in the conversation; don't repeat long summaries.
- Short, direct answers; no unrequested explanations.
- Prefer targeted edits over rewriting whole files.
- Suggest `/compact` when the conversation gets long, and `/clear` when switching topics.
- Suggest a smaller model (`/model`) for simple tasks when it makes sense.

## When finishing a large task in Warning/Reserve mode
State in one line the current usage (if available) and how much is left before the reserve limit.
