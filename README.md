# token-reserve / reserva-tokens

Claude Code plugin that keeps a reserve of your plan limit (default 20%) for emergencies.
Available in two languages — install only one.

| Language | Plugin | Install | Docs |
|---|---|---|---|
| English | `token-reserve` | `/plugin install token-reserve@reserva-tokens` | [README](plugins/token-reserve/README.md) |
| Português | `reserva-tokens` | `/plugin install reserva-tokens@reserva-tokens` | [README](plugins/reserva-tokens/README.md) |

First add the marketplace:

```
/plugin marketplace add brugodoi/reserva-tokens
```

Then run `/token-reserve:setup` (or `/reserva-tokens:setup`) and restart Claude Code.

## License

MIT
