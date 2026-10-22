<p align="center">
  <img src="assets/icon.svg" alt="astro" width="112">
</p>

# astro

Plugin de desenvolvimento com IA para o Claude Code. É uma esteira que vai do
contrato de trabalho até o Pull Request, com um gate de segurança que bloqueia
comandos perigosos na hora de executar.

O nome do plugin (`astro`) é o namespace dos comandos: cada skill aparece como
`astro:<nome>`.

## Instalação

Pelo marketplace no GitHub:

```bash
/plugin marketplace add bellinivitor/astro
/plugin install astro@astro
```

As skills passam a existir como `/astro:setup`, `/astro:plan` e assim por diante.
Rode `/astro:help` para ver o guia.

Para desenvolver o próprio plugin localmente, aponte o Claude Code para a pasta do
plugin e recarregue:

```bash
claude --plugin-dir "<caminho>/astro/astro"
/reload-plugins
```

## As skills

| Comando | Fase | O que faz |
|---|---|---|
| `astro:setup` | Contrato | Grava o contrato de trabalho no `CLAUDE.md`, detecta a stack e instala o gate. Em Laravel, baixa a arquitetura e cria um `AGENTS.md` por domínio. |
| `astro:plan` | Planejar | Faz as perguntas certas, propõe um plano e, depois do seu OK, quebra o trabalho em tasks na própria sessão (sem criar arquivos no projeto). |
| `astro:exec` | Executar | Roda o plano inteiro, uma task por vez, com um commit para cada task. |
| `astro:commit` | Fechar | Escreve a mensagem no formato `TIPO: Título` com a lista de alterações, em português. |
| `astro:pr` | Fechar | Escreve a descrição do Pull Request. |
| `astro:answer` | Fechar | Gera o texto de entrega da task (comportamento, impacto, como testar e deploy) num arquivo local, pronto para copiar. |
| `astro:gate` | Gate | Abre o editor de regras do gate no navegador. Ao salvar, regenera o `astro_gate.py`. |
| `astro:help` | Ajuda | Mostra o guia da esteira. |

O plano do `astro:plan` é efêmero: ele vive na lista de tarefas da sessão, não em
arquivos `.md` no projeto. Os commits do `astro:exec` ficam só com código.

## O gate de segurança

O contrato orienta por texto, mas o gate garante por código. Toda execução de
comando é inspecionada e bloqueada se contiver um padrão proibido, como
`migrate:fresh`, `rm -rf`, `git push --force` ou `truncate`.

As regras ficam num SQLite editável. Rode `astro:gate` para abrir a interface no
navegador, ajuste as regras e clique em Gerar gate. Isso reescreve o arquivo
`.claude/hooks/astro_gate.py`, que é instalado como hook `PreToolUse`. O arquivo
gerado é autossuficiente, então também roda como CLI na sua VM ou no seu CI.

## Camada Laravel

Quando o projeto é Laravel (tem `composer.json` e `artisan`), o `setup` aplica uma
camada extra, descrita em `astro/skills/setup/laravel.md`:

- **Laravel Boost:** usa as ferramentas MCP para pegar o contexto real do projeto
  em vez de chutar a API.
- **Barreiras de Laravel:** comandos destrutivos de artisan e migrations, testes em
  SQLite `:memory:` e fakes de mail, queue e eventos.
- **Arquitetura obrigatória:** baixa o `AGENTS.md` de `bellinivitor/laravel-architecture`
  para `docs/architecture/` e registra no `CLAUDE.md`.
- **Um `AGENTS.md` por domínio:** garante um `app/Domain/{Dominio}/AGENTS.md` com
  propósito, glossário, estados, regras, ações, contratos e dependências, para o
  agente entender cada domínio.
- **Estrutura de exceptions:** cria as bases `DomainHttpException` e
  `DomainException`, um handler global em `bootstrap/app.php` que responde
  `{ message, error_code }`, e as regras de quando lançar e capturar.
- **Domain no PSR-4:** confirma que o namespace `Domain\` está no autoload do
  `composer.json`.
- **Tradução com `__()`:** apenas em contexto Livewire.

## Estrutura do repositório

```
astro/                              repositório (marketplace)
├─ .claude-plugin/marketplace.json  catálogo que aponta para o plugin
├─ README.md
└─ astro/                           o plugin
   ├─ .claude-plugin/plugin.json    manifesto
   └─ skills/
      ├─ setup/   SKILL.md, laravel.md, ai-gate/ (app.py, gate_template.py)
      ├─ plan/    SKILL.md
      ├─ exec/    SKILL.md
      ├─ commit/  SKILL.md
      ├─ pr/      SKILL.md
      ├─ answer/  SKILL.md
      ├─ gate/    SKILL.md
      └─ help/    SKILL.md
```

## Licença

MIT. Veja o arquivo `LICENSE`.
