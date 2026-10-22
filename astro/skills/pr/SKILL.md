---
name: pr
description: >-
  Gera a descrição de um Pull Request (o que foi feito, impacto, como testar,
  pontos de atenção) e, com confirmação, abre o PR. Use quando o usuário pede
  para "abrir o PR", "descrever o PR", "montar a descrição do pull request".
---

# astro:pr — descrição de Pull Request (fase 3)

Modelo simples de descrição de PR. O foco é o **código**: o "o que muda e por
quê" já está na task, então o PR diz ao revisor **o que olhar no diff e como
validar**.

PR pequeno é revisado de verdade. PR gigante recebe "LGTM" sem ninguém ler.
Quebre quando der.

## Passo 1 — Revise o diff

- Veja tudo que vai no PR (`git diff <base>...HEAD`). **Auto-revise o diff
  inteiro** — a responsabilidade é de quem abre, não da IA.
- **Escopo único:** evite refactor + feature + fix no mesmo PR.
- Marque mudanças sensíveis: migrations, permissão/policy, integração externa que
  cobra/envia. Garanta também: sem segredos/`.env` no diff; migrations
  reversíveis e não destrutivas.

## Passo 2 — Escreva a descrição

```markdown
## O que foi feito
- <mudança técnica: arquivo, classe, endpoint, tabela>
- <...>

## Impacto
<o que mais é afetado: migration, contrato de API, job, cache,
permissão, integração externa, performance; ou "nada além do escopo">

## Como testar
1. <preparo: seed, usuário, feature flag, ambiente>
2. <passo a passo>

## Pontos de atenção / observações
<o que olhar com cuidado no diff, decisão discutível, ação para deploy, dívida deixada, o que ficou de fora; ou "nenhuma">
```

### Regras por seção

- **Título** no mesmo estilo do commit (`astro:commit`): o título da task, como
  `FEAT: Possibilitar gestão de estoque físico`.
- **O que foi feito** — fale de **código**: é o índice do diff (arquivo, classe,
  endpoint, tabela). O efeito para o usuário fica na resposta da task, não aqui.
- **Impacto** — é o que o revisor **não vê no diff**: o job que consome aquela
  tabela, o app mobile que usa aquele contrato, a query que passou a rodar em
  loop, a tabela que passa a crescer a cada operação. Escreva **simples, pro PO
  bater o olho e entender** — e **honesto**:
  - **Nenhum número que você não mediu.** Só cite magnitude ou métrica (ms, %,
    MB, nº de queries, nº de registros) se ela veio de uma **medição real**
    (benchmark, `EXPLAIN`, tamanho da migration, contagem no schema). Caso
    contrário, descreva o efeito **em palavras**: "a tabela de pedidos passa a
    crescer a cada venda" — **não** "+100 MB/mês".
  - **Sem exagero nem alarmismo.** Descreva o efeito real e provável a partir do
    diff; não invente cenário catastrófico nem use superlativo.
  - Uma linha por impacto, direto. Sem impacto além do escopo? Escreva
    **"nada além do escopo"**.
- **Como testar** é **pro revisor** — assuma que ele não conhece o contexto;
  comece pelo preparo (seed, usuário, feature flag, ambiente).
- **Pontos de atenção** — avise **explicitamente** sobre coisas sensíveis:
  migration, mudança de permissão, integração externa que envia e-mail ou cobra,
  ação necessária no deploy. Nada a destacar? Escreva **"nenhuma"**.

## Passo 3 — Abrir o PR (com confirmação)

- Só abra o PR **depois do meu OK**. Ao abrir, use `gh pr create` com o título e
  a descrição acima, apontando para a branch base correta (siga o Git flow do
  projeto). Não faça merge nem `push --force`.
