---
name: setup
description: >-
  Firma o contrato de trabalho no início de um projeto ou sessão de código com
  IA — barreiras de segurança inegociáveis, padrões de escrita (convenções,
  mudanças pequenas, testes, evidência real) e detecção da stack, persistidos no
  CLAUDE.md do projeto. Use ao iniciar ou retomar um projeto, ou quando o usuário
  pede para "definir os padrões", "firmar as regras", "fazer o setup" antes de
  escrever ou rodar código.
---

# astro:setup — contrato de trabalho (fase 0)

Antes de escrever ou rodar qualquer coisa, esta skill estabelece as regras que
valem pelo resto da sessão e as **grava no `CLAUDE.md`** para valerem sempre.
Prompt orienta; **código garante** — reforce em guardas o que for crítico. Em
dúvida, **pergunte, não invente**.

Esta é a fase 0 da esteira: `astro:setup` → `astro:plan` → `astro:exec` →
`astro:commit` / `astro:pr`.

## Passo 1 — Detecte a stack

Antes de qualquer coisa, descubra o terreno (não assuma):

- **Laravel/PHP** — existe `composer.json` + `artisan`? Então **leia
  `laravel.md` nesta mesma pasta da skill** e aplique aquela camada por cima
  destas regras. Se o Laravel Boost estiver instalado, use as ferramentas MCP
  dele para obter o contexto REAL do projeto.
- **Node/JS/TS** — `package.json`, lockfile (`package-lock.json`, `pnpm-lock`,
  `yarn.lock`), framework em `dependencies`.
- **Outra stack** — identifique gerenciador de pacotes, runner de testes e
  convenções pela estrutura de arquivos antes de codar.

Depois de detectar, situe-se: leia o código relevante e as convenções já
existentes antes de propor qualquer coisa nova.

## Passo 2 — Barreiras de segurança (não negociáveis)

Valem em qualquer stack:

- **Nada destrutivo sem confirmar.** Nunca apagar/alterar dados em massa, dropar
  ou resetar banco, `delete`/`update` sem filtro, `rm -rf`, `git push --force`.
  Parar e confirmar comigo antes.
- **Confirmar o ambiente.** Nada destrutivo fora de `local`/`testing`. **Nunca**
  em produção.
- **Não subir dependência por conta própria.** Instalar pelo lockfile
  (`install`/`ci`), nunca `update`. Não adicionar pacote sem confirmar.
- **Nunca tocar em segredos.** Não ler, logar nem colar `.env`, chaves ou
  credenciais. Usar via config no código, sem expor o valor.
- **Testes em ambiente isolado** (banco efêmero/em memória), nunca contra
  dev/prod.
- **Em dev/teste, sem efeito colateral real** — e-mail, job, notificação e HTTP
  externo vão para fakes/mocks.
- **Chamada externa que cobra, envia ou altera dados de terceiros:** parar e
  confirmar antes.
- **"Não atualizou" após uma mudança?** Suspeitar de cache antes do código.

## Passo 3 — Padrões de escrita

- **Siga as convenções que já existem** no código: nomenclatura, estrutura de
  pastas, estilo, idioma dos comentários. Código novo deve ler como o entorno.
- **Não invente** API, rota, coluna, assinatura de método ou versão. Confirme na
  fonte (docs versionadas da stack, schema real). Em dúvida, pergunte.
- **Falhas são exceptions, não retorno.** Quando um método não consegue cumprir o
  que o nome dele promete, **lance** uma exception tipada (parte do contrato) em
  vez de devolver `null`/código de erro e checar a cada passo. `catch` só onde
  houver ação concreta; senão deixe subir até a camada que decide. Não troque todo
  `if` por `throw` — caminho alternativo **esperado** é retorno normal.
- **Mudanças pequenas e revisáveis** — uma unidade lógica por vez, pensando no
  commit atômico (`astro:commit`) e no PR (`astro:pr`).
- **Testes junto.** Escreva/atualize testes e **rode a suíte**; mostre a saída
  real antes de dizer que terminou.
- **Evidência, não afirmação.** Se errou ou não tem certeza, diga — e mostre
  testes/logs reais.

## Passo 4 — Grave o contrato no CLAUDE.md

Persista as barreiras no projeto para elas valerem em **toda** sessão — o Claude
Code lê o `CLAUDE.md` automaticamente, então o contrato passa a se aplicar sem
depender de rodar esta skill de novo.

- Localize o `CLAUDE.md` na raiz do projeto; se não existir, **crie**.
- Grave **apenas** o bloco entre os marcadores abaixo. Se os marcadores já
  existirem, **substitua só o miolo entre eles** (idempotente). **Nunca** altere
  nada fora dos marcadores.
- Criar o arquivo ou o bloco do zero pode ser feito direto. Se for **sobrescrever**
  um bloco `astro:setup` que já existe, mostre antes o que muda.
- Preencha a **Stack** com o que você detectou e some as barreiras específicas
  da stack (ex.: as do `laravel.md`, se for Laravel) na lista de Seguranças.
- Se a stack tiver **arquitetura obrigatória** (ex.: Laravel — ver `laravel.md`),
  garanta o documento em `docs/architecture/` (baixando-o, se preciso) e inclua
  no bloco a linha **`Arquitetura:`** apontando para ele.

Bloco a gravar:

```markdown
<!-- astro:setup:início — gerado automaticamente; edite o miolo se precisar, mantenha os marcadores -->
## Contrato de trabalho com IA

**Stack:** <ex.: Laravel 11 · PHP 8.3 · Pest · MySQL — o que foi detectado>
<!-- se houver arquitetura obrigatória, adicione: **Arquitetura:** seguir docs/architecture/AGENTS.md -->

### Seguranças (não negociáveis)
- Nada destrutivo sem confirmar: apagar/alterar dados em massa, resetar/dropar banco, `delete`/`update` sem filtro, `rm -rf`, `git push --force`.
- Nada destrutivo fora de `local`/`testing`. Nunca em produção.
- Dependências pelo lockfile (`install`/`ci`), nunca `update`; não adicionar pacote sem confirmar.
- Nunca ler, logar ou colar `.env` nem segredos; usar via config, sem expor o valor.
- Testes em ambiente isolado (banco efêmero/em memória), nunca contra dev/prod.
- Em dev/teste, sem efeito colateral real (e-mail, job, notificação, HTTP) — usar fakes/mocks.
- Chamada externa que cobra, envia ou altera dados de terceiros: parar e confirmar.
- Se algo "não atualizou" após uma mudança, suspeitar de cache antes do código.

### Padrões
- Seguir as convenções já existentes no código.
- Não inventar API/rota/coluna/versão — confirmar na fonte; em dúvida, perguntar.
- Falhas que quebram o contrato de um método são exceptions tipadas, não retorno de erro/null; capturar só com ação concreta e deixar subir até quem decide.
- Mudanças pequenas e revisáveis; testes junto; mostrar a saída real antes de dar por pronto.
<!-- astro:setup:fim -->
```

Depois de gravar, mostre ao usuário o bloco final que ficou no `CLAUDE.md`.

## Passo 5 — Instale o gate de execução + editor (código garante)

As barreiras do Passo 2 são **prompt**; o **gate** as transforma em **guarda de
código**, barrando a execução de qualquer comando que contenha texto proibido
(`migrate:fresh`, `rm -rf`, `git push --force`, `truncate`…). As regras do gate são
editáveis por uma mini-app em `ai-gate/` (SQLite + UI web, só stdlib). Instale no
projeto — **crie o que não existir; não sobrescreva o que já existe sem avisar**:

> **Local fixo — não pergunte "onde".** O gate vai **sempre** na raiz do projeto:
> `ai-gate/`, o script em `.claude/hooks/astro_gate.py`, o hook no
> `.claude/settings.json`. Não há escolha de local a fazer. Confirme só o que é
> mesmo decisão: **sobrescrever** algo que já existe e a **edição do
> `settings.json`** (config permanente). Se a raiz do projeto for ambígua (ex.:
> monorepo), pergunte **qual** raiz — não "onde dentro dela".

- **Mini-app:** se não houver `ai-gate/` na raiz do projeto, copie a pasta
  `ai-gate/` (`app.py` + `gate_template.py`) **desta mesma pasta da skill** para a
  raiz do projeto.
- **DB + gate:** rode `python3 ai-gate/app.py --generate`. Isso cria o
  `ai-gate/rules.db` (semeado com as barreiras padrão) e gera
  `.claude/hooks/astro_gate.py` a partir dele. O **SQLite é a fonte da verdade**; o
  script é artefato **gerado** (não edite à mão).
- **Gitignore:** adicione `ai-gate/rules.db` ao `.gitignore` do projeto — o DB é
  local/editável; o que vai versionado é o gate gerado
  (`.claude/hooks/astro_gate.py`). Crie o `.gitignore` se não existir; não duplique
  a linha.
- **Hook:** garanta no `.claude/settings.json` do projeto um `PreToolUse` com
  matcher `Bash` apontando para o gate. Crie o arquivo se não existir; se existir,
  faça **merge** preservando o resto e só adicione o hook se ele ainda não estiver
  lá:

  ```json
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Bash",
          "hooks": [
            { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/astro_gate.py\"" }
          ]
        }
      ]
    }
  }
  ```

- **Editar as regras:** rode `astro:gate` (ou `python3 ai-gate/app.py`) para abrir
  a UI em `http://127.0.0.1:8787` — adicione/edite/desligue regras (regex ou texto
  literal) e clique em **Gerar gate**, que reescreve o `.claude/hooks/astro_gate.py`.
- **Fora do Claude Code** (VM/CI de execução): o `.claude/hooks/astro_gate.py` é
  **standalone** (regras embutidas, sem depender do SQLite) — copie-o e rode como
  CLI: `python3 astro_gate.py "$CMD" && eval "$CMD"`.

Confirme que pegou: um `migrate:fresh` de teste deve ser **barrado** pelo gate.

## Passo 6 — Confirme que entendeu

Para fechar o contrato, **liste em uma linha cada barreira de segurança** que
você vai respeitar nesta sessão (e, se for Laravel, as específicas do
`laravel.md`). Só então seguimos para o `astro:plan`.

## Retomar uma sessão (versão curta)

Quando o projeto já está em contexto e só quero relembrar as barreiras:

> Reforçando: confirme na fonte antes de assumir; nada destrutivo, nada de subir
> dependência, nada de tocar em `.env`/segredos; testes em ambiente isolado e com
> fakes; plano curto antes de mudanças relevantes; mostre a saída real dos testes.
