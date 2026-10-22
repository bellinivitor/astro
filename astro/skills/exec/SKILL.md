---
name: exec
description: >-
  Executa o PLANO inteiro: roda todas as tasks da sessão (do astro:plan) em ordem
  de dependência, uma a uma, com commit atômico por task,
  parando quando precisar de uma decisão sua ou algo falhar. Use quando o usuário
  pede para "executar o plano", "rodar tudo", "tocar a feature", "fazer tudo".
---

# astro:exec — roda o plano inteiro (fase 2, em lote)

Orquestra a execução de **todas** as tasks do plano do `astro:plan` (a lista de
tarefas da sessão), em ordem, uma por vez. Vale o
contrato do `astro:setup` (gravado no `CLAUDE.md`) e a arquitetura obrigatória.

## Como roda

1. **Qual plano:** o do `astro:plan` na sessão. Se não houver, rode o
   `astro:plan` antes. Se o usuário quiser rodar só parte, confirme o recorte.
2. Monte a ordem das tasks respeitando o **`Depende de`** (topológica): nunca comece
   uma task antes das dependências estarem concluídas.
3. Para **cada** task pendente, na ordem, execute-a assim: marca em andamento →
   situa → implementa só o escopo → testes → valida critérios de aceite e
   definição de pronto → marca concluída.
4. Depois de cada task concluída, faça um **commit atômico** no padrão `astro:commit`
   (um commit por task). **Não** faça `push`. Os commits ficam **só com código** — o
   plano não vira arquivo.
5. Mostre o **progresso** após cada task (ex.: `2/5 feitas — 03 em seguida`) e
   mantenha a lista da sessão atualizada. Ao concluir todas, diga que o plano
   terminou.

## Quando PARAR (não siga no automático)

- Surgiu uma **decisão que é do usuário** (não estava no plano) → pergunte
  (AskUserQuestion) e espere.
- **Testes falharam** e não dá para resolver dentro do escopo da task → pare e
  mostre a evidência real.
- A task pediria algo **destrutivo, segredo ou mudança de dependência** → barreira
  do contrato: pare e confirme.
- Uma task revelou trabalho **fora do plano** → registre como nova task na lista e
  siga; se for bloqueante, pare e alinhe.

## No fim

- Resuma o que foi feito (tasks concluídas, evidência: saída dos testes).
- Se sobrou task por fazer (por uma parada), diga o que falta e por quê.
- Sugira o `astro:pr` / `astro:answer` para fechar o conjunto.

> Uma task por vez, **em sequência** — nunca em paralelo, para manter commits
> atômicos e revisáveis.
