---
name: setup
description: Configura o plugin reserva-tokens (percentual da reserva, casos urgentes e status line de uso). Use quando o usuário pedir para configurar, instalar ou ajustar a reserva de tokens.
disable-model-invocation: true
---

# Configurar reserva-tokens

1. Pergunte ao usuário (uma única pergunta, com padrões sugeridos):
   - Percentual a manter de reserva (padrão 20).
   - Quais situações são urgentes e podem usar a reserva (ex.: "PDV parado; rede fora; servidor caído").
2. Rode o script de setup (fica em `scripts/reserva.py`, dois níveis acima do diretório base desta skill):
   `python "<diretório base desta skill>/../../scripts/reserva.py" setup --reserva N --urgente "caso 1; caso 2"`
   (use `python3` se `python` não existir).
3. Mostre a saída ao usuário e lembre que é preciso reiniciar o Claude Code.

Se o usuário já tinha uma status line, ela é mantida e o uso é exibido ao lado.
Para desfazer: `python ".../scripts/reserva.py" remover`.
