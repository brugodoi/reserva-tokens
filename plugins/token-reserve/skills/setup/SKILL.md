---
name: setup
description: Configures the token-reserve plugin (reserve percentage, urgent cases and the usage status line). Use when the user asks to configure, install or adjust their token reserve.
disable-model-invocation: true
---

# Set up token-reserve

1. Ask the user (a single question, with suggested defaults):
   - Percentage to keep in reserve (default 20).
   - Which situations are urgent and may use the reserve (e.g. "production down; network outage; server crash").
2. Run the setup script (it lives in `scripts/token_reserve.py`, two levels above this skill's base directory):
   `python "<this skill's base directory>/../../scripts/token_reserve.py" setup --reserve N --urgent "case 1; case 2"`
   (use `python3` if `python` is not available).
3. Show the output to the user and remind them to restart Claude Code.

If the user already had a status line, it is kept and usage is shown next to it.
To undo: `python ".../scripts/token_reserve.py" remove`.
