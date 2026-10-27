# token-reserve

[Claude Code](https://claude.com/claude-code) plugin that keeps a **reserve of your plan limit**
(default 20%) for emergencies — e.g. urgent production analysis, store systems, network outages.

- Shows **5-hour window** and **weekly limit** usage in the status line (yellow near the limit, red in the reserve).
- Once the limit is crossed, a hook warns Claude on every message: non-urgent tasks require your confirmation.
- The `token-reserve` skill teaches Claude to work in **economy mode** (fewer reads, no subagents, short answers).

## Installation

In Claude Code:

```
/plugin marketplace add brugodoi/reserva-tokens
/plugin install token-reserve@reserva-tokens
/token-reserve:setup
```

Setup asks for the reserve percentage and what counts as urgent, then configures the status line.
If you already have a status line, it is kept and usage is shown next to it. Restart Claude Code at the end.

Requirement: Python 3 on PATH (`python` or `python3`).

## Configuration

`~/.claude/token-reserve/config.json`:

```json
{
  "reserve": 20,
  "warning": 15,
  "urgent": ["production down", "network outage", "server crash"]
}
```

## Uninstall

```
python ~/.claude/token-reserve/token_reserve.py remove
/plugin uninstall token-reserve@reserva-tokens
```

## Limitations

- Usage comes from the `rate_limits` field Claude Code sends to the status line (Pro/Max plans). Without it nothing is shown and reserve mode never triggers — use `/usage`.
- The value updates when the status line redraws; it is an approximation, not a hard block.

## License

MIT
