---
name: answer
description: >-
  Gera o texto de resposta/entrega de uma task — o que foi feito (em
  comportamento), impacto em números, como testar, deploy, pendências — e grava
  num ARQUIVO local (nunca só no terminal, nunca commitável) para copiar sem
  quebrar a formatação. Use quando o usuário pede para "responder a task",
  "resposta da task", "texto de entrega", "fechar a task pro QA".
---

# astro:answer — resposta da task (fase 3)

Serve para quem for **testar** entender o que foi feito sem te chamar no chat, e
para quem for **subir** saber o que a mudança custa. Escreva pensando em quem não
acompanhou o desenvolvimento: o QA, o PO, ou você mesmo daqui a dois meses.

## Passo 1 — Grave num arquivo (não no terminal)

Markdown colado do terminal **quebra a formatação**. Então a resposta vai sempre
para um **arquivo**, fácil de achar e **sem risco de ser commitado**:

- **Onde:** `entregas/<branch>.md` na raiz do repo (`git rev-parse --show-toplevel`).
  Um arquivo por branch (troque `/` por `-` no nome). Se já existir, atualize.
- **Sem risco de commit:** `entregas/` entra no ignore **local** do repo
  (`.git/info/exclude`), que **não é versionado** — nunca no `.gitignore` (esse
  seria commitado). Faça de forma idempotente e confirme que está ignorado:

  ```bash
  root=$(git rev-parse --show-toplevel)
  mkdir -p "$root/entregas"
  grep -qxF 'entregas/' "$root/.git/info/exclude" 2>/dev/null \
    || echo 'entregas/' >> "$root/.git/info/exclude"
  git -C "$root" check-ignore -q entregas/ && echo "ok: entregas/ ignorado localmente"
  ```

- **Nunca** dê `git add` nesse arquivo; confirme no `git status` que ele não
  aparece como alteração.
- Fora de um repo git, apenas grave em `entregas/` — não há o que commitar.
- Ao terminar, **mostre o caminho absoluto** do arquivo; se o ambiente permitir
  abrir/entregar arquivos, abra-o para o usuário copiar o markdown limpo.

## Passo 2 — Preencha o template

```markdown
### O que foi feito
<resumo dos requisitos implementados>

### Impacto
- Dados: <+X MB em 30 dias, de N linhas/dia × Y KB por linha; ou "não cresce">
- Banco: <+N queries por request, índice novo, migration em tabela de M linhas>
- Performance: <endpoint/job: Xms antes, Yms depois>
- Contratos: <endpoint, payload ou evento alterado, e quem consome>
- Infra e custo: <fila, worker, storage, chamada a serviço pago>

### Como testar
1. <passo a passo, incluindo usuário/ambiente se necessário>
2. <...>
Resultado esperado: <o que deve acontecer>

### Deploy
<o que precisa acontecer fora do merge: ordem de subida, migration
demorada, backfill, variável de ambiente, feature flag, invalidar
cache, e como reverter se der errado>

### O que ficou de fora
<o que não entrou nesta entrega e por quê; ou "nada">

### Observações
<decisões tomadas, dúvidas, dívidas deixadas; ou "nenhuma">

Branch: <nova-branch>
Branch origem: <branch>

---

PRs: <links>
```

## Passo 3 — Regras de escrita

- **Comportamento, não código.** "Agora o cliente recebe e-mail ao aprovar o
  pedido" é melhor que "adicionei o `OrderApprovedListener`". **Exceção:** o
  impacto — ali número é melhor que frase.
- **O caminho é o fluxo principal**, escrito para quem não conhece o contexto.
  Casos de erro e borda entram em **Observações**.
- Se precisou de **dado de teste** (usuário com cargo, produto, cupom), informe
  qual usar.
- Se mudou **algo que não estava na task**, registre aqui — surpresa em QA gera
  retrabalho.
- Se algo **ficou pendente**, diga na hora de entregar, não depois que voltou
  reprovada.
- Preencha **Deploy** sempre que subir não for só apertar o botão: migration
  longa, ordem entre serviços, variável nova, executar query, etc.

## Impacto em números

Estimativa vale mais que adjetivo. "Pode pesar o banco" não dá para avaliar.
"+2,4 GB em 30 dias" dá. **Ordem de grandeza basta** — o que importa é a diferença
entre 2 MB e 2 GB.

> Diferente do `astro:pr` (onde o impacto é simples, pro PO, sem número que você não
> mediu), **aqui o número é bem-vindo** — desde que seja medido **ou** venha com a
> conta e a suposição escritas.

Como chegar no número sem perder meia hora:

- **Crescimento de tabela** = linhas/dia × tamanho da linha × 30. O volume diário
  sai de uma tabela parecida que já existe. No Postgres, o tamanho médio da linha
  sai de algo como `pg_total_relation_size('tabela') / count(*)`.
- **Queries por request:** coloque um log de query temporário no endpoint, antes e
  depois. Salto de 3 para 40 é **N+1**, não otimização pendente.
- **Tempo:** meça o endpoint ou job com dado parecido com produção. 200 registros
  em dev não dizem nada sobre 200 mil.
- **Custo externo:** chamadas/dia × preço por chamada. Vale para API paga, SMS,
  e-mail, storage.
- **Se não dá para medir agora**, escreva a conta e a suposição: "estimo 40k
  linhas/dia assumindo o mesmo volume de pedidos de hoje". Suposição escrita
  alguém corrige; número ausente ninguém questiona.

**Exemplo:**

```markdown
### Impacto
- Dados: +2,4 GB em 30 dias na stock_movements (40k linhas/dia × 2 KB)
- Banco: +1 query na listagem de produtos; índice novo em (deposito_id, produto_id)
- Performance: GET /produtos 180ms antes, 210ms depois, com 50k produtos
- Contratos: payload de /produtos ganha o campo saldo_por_deposito (mobile ignora campo extra)
- Infra e custo: nada
- Permissão: perfil Estoquista passa a acessar /depositos
```
