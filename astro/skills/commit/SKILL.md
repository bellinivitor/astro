---
name: commit
description: >-
  Escreve a mensagem de commit no formato "TIPO: Título" + lista de alterações em
  português (particípio passado) e cria o commit de UMA mudança lógica. Use
  quando o usuário pede para "commitar", "fazer o commit", "gerar a mensagem de
  commit" depois de uma unidade de trabalho pronta.
---

# astro:commit — mensagem de commit (fase 3)

Gera uma mensagem de commit **clara e padronizada**. Um commit = **uma mudança
lógica** (se a descrição pede "e", provavelmente são dois commits).

## Passo 1 — Veja o que vai entrar

- `git status` e `git diff --staged` (ou `git diff`) para revisar a mudança.
- Se houver mais de uma unidade lógica misturada, separe com stage seletivo
  (`git add -p`) — um commit por unidade.
- **Nada de segredo/`.env` no diff.** Auto-revise antes.

## Passo 2 — Monte a mensagem

Você é um especialista em criar mensagens de commit claras e padronizadas. Gere
a mensagem seguindo **exatamente** este formato:

```
<TIPO>: <Título curto e objetivo>
- <Alteração 1>
- <Alteração 2>
- <Alteração 3>
- ...
```

**Regras:**

- O título deve **resumir a principal entrega**.
- O **tipo** deve ser um dos seguintes:
  - `FEAT`: Nova funcionalidade.
  - `FIX`: Correção de bug.
  - `REFACTOR`: Refatoração sem alteração de comportamento.
  - `PERF`: Melhoria de performance.
  - `TEST`: Adição ou alteração de testes.
  - `DOCS`: Alteração de documentação.
  - `CHORE`: Tarefas de manutenção, configuração ou dependências.
  - `CI`: Alterações em CI/CD.
  - `BUILD`: Alterações de build ou empacotamento.
  - `STYLE`: Ajustes de formatação ou estilo sem alterar lógica.
- A descrição deve estar em **português**.
- O commit descreve uma alteração **já realizada**, então o título e os itens da
  lista devem ser escritos no **particípio passado**, concordando em gênero e
  número com o que foi feito (ex.: Implementado, Implementada, Corrigido,
  Corrigida, Adicionado, Adicionada, Removido, Removida, Refatorado, Refatorada,
  Criado, Criada, Atualizado, Atualizada, Registrado, Registrada).
- **Nunca** use verbo no infinitivo (ex.: não usar "Implementar", "Corrigir",
  "Adicionar").
- A lista deve conter **apenas as alterações implementadas**, uma por linha.
- **Não explique** o commit, apenas retorne a mensagem final.
- Seja **específico** e evite itens genéricos como "ajustes diversos".

**Exemplo de saída:**

```
FEAT: Implementada gestão de estoque físico

- Adicionado cadastro de estoques físicos
- Implementada movimentação de entrada de produtos
- Implementada movimentação de saída de produtos
- Criada validação de saldo disponível
- Exibido histórico de movimentações
- Adicionados testes para regras de movimentação
```

## Passo 3 — Commit

- Crie o commit com a mensagem. **Não** faça `push` (e nunca `--force`).
- **Não** adicione trailer de co-autoria nem qualquer menção à IA na mensagem.
