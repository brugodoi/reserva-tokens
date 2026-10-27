# reserva-tokens

Plugin do [Claude Code](https://claude.com/claude-code) que mantém uma **reserva do limite do plano**
(padrão 20%) para emergências — ex.: análises urgentes de produção, PDVs, rede.

- Mostra o uso da **janela de 5h** e do **limite semanal** na status line (amarelo perto do limite, vermelho na reserva).
- Ao passar do limite, um hook avisa o Claude a cada mensagem: tarefas não urgentes passam a exigir sua confirmação.
- A skill `reserva-tokens` ensina o Claude a trabalhar em **modo econômico** (menos leituras, sem subagentes, respostas curtas).

## Instalação

No Claude Code:

```
/plugin marketplace add brugodoi/reserva-tokens
/plugin install reserva-tokens@reserva-tokens
/reserva-tokens:setup
```

O setup pergunta o percentual da reserva e o que conta como urgente, e configura a status line.
Se você já tem uma status line, ela é mantida e o uso aparece ao lado. Reinicie o Claude Code no final.

Requisito: Python 3 no PATH (`python` ou `python3`).

## Configuração

`~/.claude/reserva-tokens/config.json`:

```json
{
  "reserva": 20,
  "atencao": 15,
  "urgente": ["PDV parado", "rede fora", "servidor caído"]
}
```

## Desinstalar

```
python ~/.claude/reserva-tokens/reserva.py remover
/plugin uninstall reserva-tokens@reserva-tokens
```

## Limitações

- O uso vem do campo `rate_limits` que o Claude Code envia à status line (planos Pro/Max). Sem ele, nada é exibido e o modo reserva não dispara — use `/usage`.
- O valor é atualizado quando a status line é redesenhada; é uma aproximação, não um bloqueio rígido.

## Licença

MIT
