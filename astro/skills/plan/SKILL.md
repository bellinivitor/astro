---
name: plan
description: >-
  Modo de planejamento antes de codar: situa-se no projeto, esclarece as decisões
  do usuário com AskUserQuestion, apresenta um plano para aprovação e, só depois do
  OK, decompõe o plano em tasks na lista de tarefas da SESSÃO (sem criar arquivos no
  projeto). Use quando o usuário descreve uma feature ou mudança e antes de
  implementar, ou quando pede para "planejar", "quebrar em tasks", "montar o plano".
---

# astro:plan — do pedido ao plano (fase 1)

Antes de escrever código há um **momento de planejamento**: você se situa, pergunta
o que for decisão do usuário e só então propõe um plano que ele aprova. O objetivo é
ser **assertivo** — acertar o alvo na primeira vez em vez de gerar código no escopo
errado e refazer.

O plano é **efêmero**: vive na **lista de tarefas da sessão**, não em arquivos `.md`
no projeto. Nada de `tasks/` versionado — os commits ficam só com código.

Fase 1 da esteira: vem depois do `astro:setup` e antes do `astro:exec`.

> **Regra de ouro:** pergunte o que é **decisão do usuário**; **decida o resto**
> (com default seguro, dizendo a suposição). Perguntar tudo vira interrogatório;
> assumir tudo gera retrabalho.

## Passo 1 — Entre em modo de planejamento (não escreva código)

Situe-se antes de propor qualquer coisa:

- Use as ferramentas da stack para ver o que já existe (ex.: Laravel Boost —
  `search-docs`, `application-info`, `list-routes`, `database-schema`).
- Leia o código relevante e as convenções do projeto.
- **Não escreva nem altere código ainda.**

## Passo 2 — Esclareça as decisões (AskUserQuestion)

Para **cada decisão genuinamente do usuário** — que você não consiga inferir do
código/docs nem resolver com um default óbvio — use a ferramenta
**AskUserQuestion**:

- Uma pergunta objetiva por decisão; **2 a 4 opções** concretas e mutuamente
  exclusivas.
- A **recomendada primeiro**, marcada `(recomendada)`, com uma linha de porquê.
- Múltipla escolha quando as opções não forem exclusivas.
- Um header curto por pergunta (ex.: "Banco", "Auth", "Escopo").

**NÃO pergunte** o que dá pra descobrir no código/docs nem o que tem default
seguro — nesses casos decida e avise a suposição em uma linha.

| Perguntar (decisão do usuário) | Decidir (e só avisar) |
|---|---|
| Regra de negócio ambígua | O que dá pra ver no código/schema/docs |
| Trade-off sem resposta única (fila vs síncrono, soft delete vs apagar) | Convenção que o projeto já segue |
| Escopo / prioridade (incluir X agora ou depois?) | Detalhe de implementação com default seguro |
| Algo irreversível ou caro (migration destrutiva, contrato de API) | Nomenclatura / estrutura de pastas |

> Sem AskUserQuestion no agente? Faça as **mesmas perguntas** numa lista
> numerada, cada uma com suas opções e a recomendada destacada — e espere a
> resposta antes de planejar.

## Passo 3 — Apresente o plano e espere o OK

- **Objetivo** e **critérios de aceite**.
- **Passos numerados**, com os arquivos/áreas que serão tocados.
- **Riscos**, impacto em migrations/dados e o que está **fora de escopo**.
- **Como vamos testar**.

Espere o OK antes de decompor. Se durante a execução surgir uma decisão nova
relevante, volte ao AskUserQuestion em vez de assumir.

## Passo 4 — Decomponha em tasks na lista da sessão

Depois do OK, quebre o plano numa **lista ordenada de tasks** e registre-a como a
**lista de tarefas da sessão** (a todo list do agente). **Não crie arquivos no
projeto** — nada de `tasks/`, `00-index.md` nem um arquivo por task.

Cada task é um item da lista, com:

- **Título** curto (o que entrega) e a **ordem**.
- **Depende de** — quais tasks anteriores precisam estar prontas (o `astro:exec`
  respeita isso).
- **Critérios de aceite** e **fora de escopo** resumidos. Cada task ≈ 1 commit.

Guarde junto, no plano da sessão, o **objetivo**, os **critérios de aceite** gerais
e as **decisões** tomadas no AskUserQuestion — é o contexto que o `astro:exec`
vai usar.

**NÃO comece a implementar.** O usuário escolhe quando rodar — aí entra o
`astro:exec` (roda o plano todo, uma task por vez).

> O plano é da sessão: se ela fechar, ele some. Precisa **retomar depois** ou
> **revisar com o time**? Peça — aí registramos o plano num lugar (ex.: um arquivo
> local, como no `astro:answer`), em vez de poluir o repo.

## Lembre do contrato

Continua valendo o contrato do `astro:setup` (gravado no `CLAUDE.md`): nada
destrutivo, sem segredos, mudanças pequenas, evidência real.
