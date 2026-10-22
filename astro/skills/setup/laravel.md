# Camada Laravel + Boost

Aplique isto **por cima** das regras genéricas do `SKILL.md` quando o projeto
for Laravel (`composer.json` + `artisan`).

## Use o Boost antes de assumir

O [Laravel Boost](https://laravel.com/docs/boost) é um MCP server oficial que dá
acesso ao contexto REAL do projeto e à documentação **versionada**. Se estiver
instalado, use as ferramentas dele:

- **`search-docs`** — confirme a API da versão EXATA do projeto antes de usar.
  Nunca invente assinatura de método.
- **`application-info` / `list-routes` / `database-schema` /
  `list-artisan-commands`** — entenda o que já existe antes de criar algo novo.
- **`read-log-entries` / `last-error` / `browser-logs`** — leia o erro REAL ao
  investigar um bug, não adivinhe a causa.
- **`database-query`** — somente leitura (read-only por design). Prefira a
  `tinker` quando só precisa consultar.
- **`tinker`** — executa PHP arbitrário (acesso total). Use SÓ para leitura
  (`count`, `first`, `get`); desconfie de qualquer escrita.
- **`list-available-env-vars`** — mostra os NOMES das variáveis, nunca os
  valores. Continue sem ler/colar o conteúdo do `.env`.

## Barreiras específicas de Laravel

Somam-se às genéricas:

- **Comandos destrutivos proibidos sem confirmar:** `migrate:fresh`,
  `migrate:refresh`, `migrate:reset`, `db:wipe`, `queue:flush`/`queue:clear`,
  `truncate()`, `delete()`/`update()` SEM `where`, `forceDelete()`.
- **Dependências:** `composer install` / `npm ci` — nunca `composer update` /
  `npm update` por conta própria.
- **Ambiente:** confirme `APP_ENV` = `local`/`testing` antes de agir.
- **Testes** rodam só no **SQLite `:memory:`** — nunca contra o banco de
  dev/prod.
- **Fakes em dev/teste:** `Mail::fake()`, `Queue::fake()`,
  `Notification::fake()`, `Event::fake()`, `Http::fake()`.
- **Cache:** se algo "não atualiza" após uma mudança, rode `config:clear` /
  `route:clear` / `optimize:clear` antes de suspeitar do código.

## Arquitetura do projeto (obrigatória)

Todo projeto Laravel segue a arquitetura domain-driven definida em
**https://github.com/bellinivitor/laravel-architecture** (`AGENTS.md`). Ela é
**inegociável** — organize todo código novo conforme ela.

Durante o setup:

1. **Garanta o documento no projeto.** Se ainda não existir `docs/architecture/AGENTS.md`,
   baixe de
   `https://raw.githubusercontent.com/bellinivitor/laravel-architecture/main/AGENTS.md`
   e salve em **`docs/architecture/AGENTS.md`** (fica versionado e disponível
   offline). Se já existir, **não sobrescreva** sem avisar. Se não conseguir
   baixar, referencie a URL no `CLAUDE.md` e siga a arquitetura mesmo assim.
2. **Registre no `CLAUDE.md`** (dentro do bloco `astro:setup`) a linha:
   `**Arquitetura:** seguir docs/architecture/AGENTS.md (domain-driven — bellinivitor/laravel-architecture)`.
3. **Certifique o autoload PSR-4 do `Domain`.** Confirme que o namespace
   `Domain\` está mapeado no `composer.json` (`autoload.psr-4`), apontando para a
   pasta do domínio (ex.: `"Domain\\": "app/Domain/"`). Se faltar, adicione o
   mapeamento e rode `composer dump-autoload`, avisando o que mudou.
4. **Garanta um `AGENTS.md` por domínio.** Para cada `app/Domain/{Dominio}/`,
   confirme que existe um `app/Domain/{Dominio}/AGENTS.md` explicando o domínio
   para os agentes. Se faltar, crie a partir do template da seção **AGENTS.md do
   domínio** abaixo, preenchendo o que der para inferir do código e marcando o
   resto como `TODO`; **não sobrescreva** um existente sem avisar. Registre no
   `CLAUDE.md` (bloco `astro:setup`) a linha: `**Domínios:** cada app/Domain/{Dominio}
   tem um AGENTS.md — leia o do domínio antes de mexer nele e atualize-o quando o
   comportamento mudar.`

Pontos inegociáveis (o detalhe e os exemplos estão no doc baixado — leia-o antes
de codar):

- **Pipeline:** Route → FormRequest → Controller → Action → Resource. Controllers
  finos (só autorização, montagem de DTO e chamada da Action).
- **Lógica de negócio só em Actions** (`readonly class`, um `__invoke()`, uma
  responsabilidade). Actions recebem **DTOs**, nunca Requests; escritas sempre em
  **transação**.
- **Camada `Domain/{Dominio}/`**: Actions, DataTransferObjects, QueryBuilders,
  Enums, Resources, States, Policies, Notifications, Jobs, Collections. O Domain
  não lida com HTTP. Cada domínio tem também um **`AGENTS.md`** na raiz (ver
  seção **AGENTS.md do domínio**).
- **Sem Repository** — usar **QueryBuilders** customizados (estendem o Builder).
- **Respostas de API sempre via Resources**, nunca model cru.
- **Injeção direta de classes concretas** (sem interface de implementação única).
- **PHP moderno**: `readonly`, enums backed, constructor promotion. **Código em
  inglês**.
- **Tradução (`__()`):** use **apenas** em contexto **Livewire** (componentes/
  views). Fora do Livewire (ex.: respostas de API), **não** use `__()` — isto
  refina a regra de tradução da arquitetura.
- **Erros:** exceptions tipadas de domínio — `DomainHttpException` (API) e
  `DomainException` (background). Bases, handler e regras na seção **Estrutura de
  exceptions** abaixo (o setup faz o scaffold).
- **Testes:** unitários isolam Actions/DTOs (Arrange→Act→Assert); feature testam
  o fluxo HTTP ponta a ponta.

Antes de dar qualquer task por pronta, rode o **checklist de implementação** do
próprio `AGENTS.md`.

## AGENTS.md do domínio

Cada `app/Domain/{Dominio}/` tem um **`AGENTS.md`** na raiz — a visão que um
agente (ou um dev novo) lê **antes de mexer** ali, para entender o que o domínio
faz sem reconstruir tudo pelo código. É o `AGENTS.md` mais próximo, carregado
automaticamente ao trabalhar na pasta.

Mantenha-o **curto e de alto sinal**: preencha só as seções que o domínio tem
(seção vazia some) e **atualize quando o comportamento mudar** — doc
desatualizada engana mais que ausência. Descreva **comportamento, regras e
fronteiras**, não o código linha a linha.

Template:

```markdown
# Domínio {Nome}

## Propósito
<1-2 frases: a capacidade de negócio que este domínio cobre.>
**Fora do escopo:** <o que NÃO é responsabilidade dele; a fronteira com outros domínios.>

## Linguagem (glossário)
- **<Termo>**: <significado no domínio, sem ambiguidade.>

## Modelos principais
- **<Model>** (`tabela`): <o que representa e as relações-chave.>

## Estados e transições
<Status possíveis e as transições VÁLIDAS (não invente transição fora disto); ou "sem máquina de estado".>

## Regras de negócio / invariantes
- <o que precisa ser sempre verdade; validações inegociáveis do domínio.>

## Ações (casos de uso)
- **<Action>**: <o que faz, DTO de entrada e efeito; roda em transação.>

## Contratos expostos
- **API:** <endpoints/Resources que outros consomem.>
- **Eventos / Jobs / Notifications:** <o que dispara e quem reage.>

## Dependências
- **Usa:** <outros domínios e serviços externos.>
- **É usado por:** <quem depende deste domínio.>

## Exceptions
- **<ClasseException>** (`ERROR_CODE`): <quando é lançada.>

## Permissões
- <Policies/perfis: quem pode o quê; ou "sem restrição específica".>

## Pontos de atenção
- <armadilhas, decisões não óbvias, idempotência, efeitos colaterais, dívidas.>

## Como testar
- <factories/seeds e dados típicos para exercitar o domínio.>
```

Ao criar um domínio novo (durante uma task), crie o `AGENTS.md` dele junto.

## Estrutura de exceptions

Exceptions não são só para erro: são **controle de fluxo**. Quando um método não
consegue cumprir o que o nome dele promete, ele **lança** — não devolve um "meio
sucesso" nem `null` para ser checado a cada passo. A exception sobe até a camada
que tem uma decisão a tomar: a **regra de negócio decide que** algo falhou, a
**infra decide como** apresentar.

> Não troque todo `if` por `throw`. Caminho alternativo **esperado** é retorno
> normal (ex.: `User::find($id) ?? User::guest()`), não exception.

### As duas bases (scaffold no setup)

Durante o setup, **garanta que as bases existam** em
`app/Domain/Shared/Exceptions/` — crie se faltarem (idempotente; não sobrescreva
sem avisar). Critério para escolher: *"Essa exception é parte do contrato HTTP que
o cliente da API deve receber?"* — **Sim** → `DomainHttpException`; **Não** →
`DomainException`.

- **`DomainHttpException`** — situações que o consumidor da API deve receber como
  parte do contrato (cliente bloqueado, saldo insuficiente, recurso não
  encontrado, permissão negada). Estende a `HttpException` do Symfony.
- **`DomainException`** — falhas de processo fora do HTTP (jobs de fila, comandos
  Artisan, sincronização em background, invariantes internas). Estende
  `RuntimeException`. Em request HTTP **não** vire erro de negócio: deixe o Laravel
  responder 500.

```php
namespace Domain\Shared\Exceptions;

use Symfony\Component\HttpKernel\Exception\HttpException;

abstract class DomainHttpException extends HttpException
{
    public function __construct(?string $message = null)
    {
        parent::__construct(
            statusCode: $this->status(),
            message: $message ?? $this->defaultMessage(),
        );
    }

    abstract public function errorCode(): string;

    protected function status(): int
    {
        return 422;
    }

    protected function defaultMessage(): string
    {
        return 'Não foi possível concluir a operação.';
    }
}
```

```php
namespace Domain\Shared\Exceptions;

use RuntimeException;

abstract class DomainException extends RuntimeException
{
    abstract public function errorCode(): string;
}
```

### Exceptions concretas

Uma classe por situação, **`final`**, em `app/Domain/{Dominio}/Exceptions/`, nome
terminando em `Exception`. Cada uma tem um **`errorCode()`** estável em
`UPPER_SNAKE_CASE` — é o contrato que o frontend lê; a `message` é para humanos e
pode mudar. Mensagem em **string pura** (nada de `__()` fora do Livewire).

```php
namespace Domain\Payment\Exceptions;

use Domain\Shared\Exceptions\DomainHttpException;
use Symfony\Component\HttpFoundation\Response;

final class InsufficientBalanceException extends DomainHttpException
{
    public function errorCode(): string
    {
        return 'INSUFFICIENT_BALANCE';
    }

    protected function status(): int
    {
        return Response::HTTP_UNPROCESSABLE_ENTITY;
    }

    protected function defaultMessage(): string
    {
        return 'Saldo insuficiente para concluir a operação.';
    }
}
```

```php
namespace Domain\Invoice\Exceptions;

use Domain\Shared\Exceptions\DomainException;

final class InvoiceSyncFailedException extends DomainException
{
    public function errorCode(): string
    {
        return 'INVOICE_SYNC_FAILED';
    }
}
```

Lançar fica legível e autodocumentado — o nome do método sinaliza a interrupção:

```php
$customer = $this->customers->findOrFail($id);

$customer->assertNotBlocked();
$customer->assertHasCredit($value);

return $this->createOrder($customer, $value);
```

### Handler global (scaffold no setup, só na 1ª vez)

Um **único** ponto converte `DomainHttpException` em JSON padronizado
`{ message, error_code }` — o controller nunca formata erro. No Laravel 11/12,
registre em `bootstrap/app.php`. **Só no primeiro setup:** se o `render` ainda não
existir, crie-o; depois disso, **não mexa no handler** — o setup não reescreve o
que já está lá:

```php
use Domain\Shared\Exceptions\DomainHttpException;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Http\Request;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->render(function (DomainHttpException $e, Request $request) {
        if ($request->expectsJson()) {
            return response()->json([
                'message' => $e->getMessage(),
                'error_code' => $e->errorCode(),
            ], $e->getStatusCode());
        }
    });
})
```

`DomainException` (e qualquer `RuntimeException`) **não** é renderizada aqui: em
HTTP vira 500; em job, deixa o processo falhar para a fila aplicar retry e
`failed_jobs`. **Nunca** capture `RuntimeException` num job só para logar — isso
finge sucesso.

> **Divergência conhecida com a arquitetura:** o `docs/architecture/AGENTS.md`
> hoje diz *não mexer no handler* e usa o formato padrão do Laravel (`{ message }`,
> sem `error_code`). Esta skill segue o **artigo** (mais recente): handler próprio
> com `error_code`. É **intencional** — alinhe os dois documentos quando atualizar
> a arquitetura. Num projeto que **já tem** o handler, não sobrescreva: crie só se
> faltar e avise a divergência.

### Como capturar

- **`catch` só com ação concreta** no ponto (fallback de provedor, traduzir a
  exception, compensar, continuar um lote, reagendar o job, liberar recurso). Se a
  ação seria só "logar e devolver 500", **não capture** — o handler global já faz.
- **Capture o tipo específico**, nunca `Exception`/`Throwable` genérico; ordene os
  `catch` do mais específico para o mais genérico. Bugs (`TypeError`, falha de
  banco) devem continuar subindo.
- **Traduza** exceptions de terceiros para o domínio preservando a original em
  `previous:`.
- **Relançe** (`throw $e;`) quando a camada atual faz uma ação local mas não é
  quem resolve.
- **Transação:** lançar dentro de `DB::transaction(...)` já faz rollback
  automático — não precisa de `rollBack()` nem `catch`.

```php
try {
    return $this->primaryProvider->rate($currency);
} catch (ProviderUnavailableException $e) {
    Log::warning('Provedor primário fora do ar, usando fallback.', [
        'error_code' => $e->errorCode(),
    ]);

    return $this->fallbackProvider->rate($currency);
}
```

### Registre no CLAUDE.md

No bloco `astro:setup`, dentro de **Padrões**, acrescente a linha específica da
stack:

> - Exceptions tipadas de domínio: `DomainHttpException` (API → JSON `{ message, error_code }` pelo handler em `bootstrap/app.php`) e `DomainException` (background → job falha); `errorCode()` estável em UPPER_SNAKE; `catch` só com ação concreta; bugs sobem.

## Guidelines do Boost

O `boost:install` instala AI guidelines compostas por pacote (Laravel, Livewire,
Inertia, Pest, Filament, Pennant…) e cientes da versão. O agente as lê como
contexto — some com as regras deste contrato e siga as convenções idiomáticas do
framework.
