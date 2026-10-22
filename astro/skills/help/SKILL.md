---
name: help
description: >-
  Explica a esteira astro: o que cada skill faz, a ordem de uso e o fluxo típico do
  contrato ao PR/entrega, incluindo o gate de execução. Use quando o usuário pede
  "ajuda", "help", "como usar", "o que o dev faz", "quais comandos", ou chama
  astro:help.
---

# astro:help — como usar a esteira

A esteira `astro:` é um conjunto de skills pra desenvolver com IA **do contrato ao
PR/entrega**, com uma guarda de código (o **gate**) fazendo valer as barreiras de
segurança. Cada skill é uma fase; use na ordem, mas chame só o que precisar.

## A esteira em uma olhada

| Fase | Comando | Quando usar |
|---|---|---|
| 0 · contrato | `astro:setup` | Ao iniciar/retomar um projeto, antes de escrever código. |
| 1 · planejar | `astro:plan` | Descreveu uma mudança e quer um plano antes de implementar. |
| 2 · executar | `astro:exec` | Roda o **plano inteiro**, uma task por vez. |
| 3 · fechar | `astro:commit` | Gerar a mensagem e commitar uma mudança lógica. |
| 3 · fechar | `astro:pr` | Montar a descrição do Pull Request. |
| 3 · fechar | `astro:answer` | Texto de entrega da task pro QA/PO (arquivo local). |
| gate | `astro:gate` | Abrir o editor de regras do gate no navegador. |
| ajuda | `astro:help` | Este guia. |

## Fluxo típico

1. **`astro:setup`** (uma vez por projeto) — firma o contrato no `CLAUDE.md`
   (barreiras + padrões), detecta a stack e, em Laravel, baixa a arquitetura e
   garante um `AGENTS.md` por domínio. Instala o **gate**: a mini-app `ai-gate/`
   (SQLite) gera o `.claude/hooks/astro_gate.py` e registra o hook que **barra
   comando proibido**.
2. **`astro:plan`** — você descreve a mudança; ele se situa, pergunta só o que é
   **decisão sua** (AskUserQuestion), propõe um plano e, após o seu OK, decompõe em
   **tasks na sessão** (sem criar arquivos no projeto).
3. **`astro:exec`** — roda o plano, uma task por vez, implementando só o escopo,
   seguindo o contrato e a arquitetura, com testes de verdade (saída real).
4. **`astro:commit`** — mensagem no formato `TIPO: Título` + lista de alterações
   (pt-BR, particípio passado); um commit por mudança lógica.
5. Fechar: **`astro:pr`** (descrição do PR) e/ou **`astro:answer`** (texto de
   entrega pro QA/PO, gravado num arquivo local não-commitável).

## O gate (código garante)

O prompt orienta, o gate **garante**: toda execução de comando é inspecionada e
**barrada** se contiver texto proibido (`migrate:fresh`, `rm -rf`,
`git push --force`, `truncate`…). As regras são editáveis:

- `astro:gate` (ou `python3 ai-gate/app.py`) abre a UI (`http://127.0.0.1:8787`)
  pra adicionar/editar/desligar regras; **Gerar gate** reescreve o
  `.claude/hooks/astro_gate.py`.
- O gate gerado é standalone — roda também como CLI na VM/CI:
  `python3 astro_gate.py "$CMD" && eval "$CMD"`.

## Princípios que valem em todas as fases

- **Pergunte o que é decisão sua; decida o resto** (com default seguro, avisando a
  suposição).
- **Confirme na fonte, não invente** API/rota/coluna/versão.
- **Mudanças pequenas e revisáveis**; testes junto; **evidência real**, não
  afirmação.
- **Nada destrutivo, sem segredos, sem subir dependência** — e o gate reforça isso.
