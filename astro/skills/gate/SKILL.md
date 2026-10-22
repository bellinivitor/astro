---
name: gate
description: >-
  Sobe a mini-app do gate (ai-gate) no navegador pra editar as regras de comandos
  proibidos; ao clicar em Gerar gate, o .claude/hooks/astro_gate.py é regenerado.
  Use quando o usuário pede "editar as regras do gate", "abrir o ai-gate", "mexer
  no gate", "gate", ou chama astro:gate.
---

# astro:gate — editor de regras do gate

Abre a mini-app `ai-gate/` (SQLite + UI web) no navegador pra editar as regras que
o gate usa pra **barrar comando proibido**. É a contraparte editável do
`astro:setup` (que instala o gate).

## Passo 1 — Confirme que o gate está instalado

- Precisa existir `ai-gate/app.py` na raiz do projeto. Se não existir, rode o
  `astro:setup` antes (ele instala o `ai-gate/` e gera o gate).

## Passo 2 — Suba o app

- Rode **`python3 ai-gate/app.py`** (porta padrão 8787; use `--port N` se estiver
  ocupada). O servidor é local (`127.0.0.1`) e fica rodando — **suba em segundo
  plano** para não bloquear a sessão.
- Abra **`http://127.0.0.1:8787`** no navegador (se o ambiente tiver navegador
  embutido, abra lá; senão, passe a URL para o usuário).

## Passo 3 — Editar e gerar

- Na UI: adicione / edite / desligue / remova regras (regex ou texto literal).
- Clique em **Gerar gate** para reescrever o `.claude/hooks/astro_gate.py` com as
  regras ativas. O **SQLite (`ai-gate/rules.db`) é a fonte da verdade**; o script é
  artefato gerado — não edite à mão.
- Ao terminar, pare o servidor (Ctrl+C no processo).

> O `astro_gate.py` gerado é standalone (regras embutidas), então roda também como
> CLI na VM/CI: `python3 astro_gate.py "$CMD" && eval "$CMD"`.
