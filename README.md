# astro — plugin `astro` (esteira de desenvolvimento com IA)

Fonte **reproduzível** das skills `astro:*` — a esteira do contrato ao Pull Request.
A documentação conceitual está nas notas irmãs (`../Esteira dev.md`,
`../Project Start.md`, `../Planejamento.md`, `../Templates/`). Aqui fica a versão
executável.

## Estrutura

```
astro/
├─ .claude-plugin/marketplace.json   catálogo local (aponta pro plugin astro)
├─ README.md                          este arquivo
└─ astro/
   ├─ .claude-plugin/plugin.json      manifesto do plugin
   └─ skills/
      ├─ setup/   SKILL.md + laravel.md + ai-gate/ (app.py + gate_template.py)
      ├─ plan/    SKILL.md
      ├─ exec/    SKILL.md
      ├─ commit/  SKILL.md
      ├─ pr/      SKILL.md
      ├─ answer/  SKILL.md
      ├─ gate/    SKILL.md
      └─ help/    SKILL.md
```

O nome do plugin (`astro`) vira o namespace: cada skill aparece como `astro:<nome>`.

## As skills

| Comando | Fase | O que faz |
|---|---|---|
| `astro:setup` | 0 · contrato | Barreiras + padrões → grava no `CLAUDE.md`; detecta a stack; em Laravel, baixa a arquitetura; instala o **gate** editável — `ai-gate/` (SQLite + UI web) gera `.claude/hooks/astro_gate.py` + hook `PreToolUse` que barra comando proibido. |
| `astro:plan` | 1 · planejar | Situa → AskUserQuestion → plano aprovado → decompõe em tasks **na sessão** (sem arquivos no projeto). |
| `astro:exec` | 2 · executar | Executa o **plano inteiro**, commit atômico por task. |
| `astro:commit` | 3 · fechar | Mensagem no formato `TIPO: Título` + lista de alterações (pt-BR, particípio passado). |
| `astro:pr` | 3 · fechar | Descrição do Pull Request. |
| `astro:answer` | 3 · fechar | Texto de entrega da task (comportamento + impacto em números + como testar + deploy) num arquivo local não commitável (`entregas/<branch>.md`), pra copiar sem quebrar. |
| `astro:gate` | gate | Abre o editor de regras do gate no navegador (`ai-gate/`); ao Gerar gate, reescreve o `astro_gate.py`. |
| `astro:help` | ajuda | Guia da esteira: o que cada skill faz, a ordem e o fluxo típico. |

O **plano** do `astro:plan` é efêmero: vive na lista de tarefas da sessão, não
em arquivos `.md` no projeto. Os commits do `astro:exec` ficam só com código.

## Instalar / reproduzir em outra conta

**A — plugin direto (recomendado):**
```bash
claude --plugin-dir "<caminho>/astro/astro"
/reload-plugins
```
As skills passam a existir como `/astro:setup`, `/astro:plan`, …

**B — marketplace (GitHub):**
```bash
/plugin marketplace add bellinivitor/astro
/plugin install astro@astro
```

**C — skills soltas (sem o namespace `astro:`):** copiar cada `astro/skills/<nome>`
para `~/.claude/skills/astro-<nome>/` e ajustar o `name:` do frontmatter para
`astro-<nome>`.

Para editar durante o desenvolvimento, mude os arquivos e rode `/reload-plugins`
(não precisa reiniciar).

## Camada Laravel

`setup/laravel.md` é aplicado quando o projeto é Laravel (`composer.json` +
`artisan`) e cobre:

- **Laravel Boost** — usar as ferramentas MCP pra contexto real (não chutar API).
- **Barreiras** de artisan/migrations, testes em SQLite `:memory:`, fakes.
- **Arquitetura obrigatória** — baixa `AGENTS.md` de
  `bellinivitor/laravel-architecture` para `docs/architecture/` e registra no
  `CLAUDE.md`.
- **`AGENTS.md` por domínio** — garante um `app/Domain/{Dominio}/AGENTS.md`
  (propósito, glossário, estados, regras, ações, contratos, dependências…) pros
  agentes entenderem cada domínio.
- **Estrutura de exceptions** — scaffold das bases `DomainHttpException` /
  `DomainException`, handler global em `bootstrap/app.php` (JSON
  `{ message, error_code }`) e regras de quando lançar/capturar.
- **Domain no PSR-4** — certifica `Domain\` no `autoload` do `composer.json`.
- **Tradução `__()`** — apenas em contexto Livewire.
