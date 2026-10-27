---
name: reserva-tokens
description: Controle de gasto de tokens com reserva obrigatória do limite do plano para emergências. Use quando o usuário perguntar sobre consumo/uso/limite de tokens, quando aparecer o aviso "[MODO RESERVA DE TOKENS]", antes de tarefas grandes (refatorações amplas, varreduras de muitos arquivos, vários subagentes, pesquisas extensas), ou quando o usuário pedir para economizar tokens.
---

# Reserva de tokens

O usuário precisa SEMPRE manter uma parte do limite do plano (janela de 5h e limite semanal)
livre para situações urgentes.

## Configuração e uso atual
- `~/.claude/reserva-tokens/config.json`: `reserva` (% a manter livre, padrão 20), `atencao`
  (margem de alerta antes do limite, padrão 15) e `urgente` (lista do que pode usar a reserva).
- `~/.claude/reserva-tokens/uso.json`: último uso conhecido (`used` = % consumido, `resets_at` = epoch do reset).
- A status line mostra `5h NN%` e `7d NN%` (amarelo na faixa de atenção, vermelho na reserva).
- O usuário pode rodar `/usage` para ver o detalhe oficial.
- Se os arquivos não existirem ou estiverem desatualizados, diga isso e sugira `/usage` ou
  `/reserva-tokens:setup` — nunca invente números.

## Faixas de operação (exemplo com reserva 20 e atenção 15)

| Uso (maior entre 5h e 7d) | Modo | Comportamento |
|---|---|---|
| < 65% | Normal | Trabalhe normalmente, mas sem desperdício. |
| 65–79% | Atenção | Modo econômico (abaixo). Antes de tarefa grande, estime o custo e avise. |
| ≥ 80% | **Reserva** | Só os casos urgentes da configuração sem perguntar. Qualquer outra coisa: informe o uso atual e quando reseta, e peça confirmação explícita antes de executar. |

Mesmo na reserva, trabalhe no modo econômico e foque em resolver a urgência primeiro.

## Modo econômico
- Não lance subagentes nem pesquisas web extensas sem o usuário pedir.
- Leia trechos de arquivos (offset/limit, grep) em vez de arquivos inteiros; logs: use `tail`/filtros.
- Não releia arquivos já vistos na conversa; não repita resumos longos.
- Respostas curtas e diretas; sem explicações que não foram pedidas.
- Prefira edições pontuais a reescrever arquivos inteiros.
- Sugira `/compact` quando a conversa estiver longa, e `/clear` ao trocar de assunto.
- Sugira modelo menor (`/model`) para tarefas simples quando fizer sentido.

## Ao terminar uma tarefa grande em modo Atenção/Reserva
Informe em uma linha o uso atual (se disponível) e quanto falta para o limite da reserva.
