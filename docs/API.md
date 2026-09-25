# Contratos REST — v1

Prefixo `/api/v1`. Esquemas completos em `/api/openapi.json`.

## Público
- `GET /entities?q=&type=&label=&cursor=&limit=&ids=` — pesquisa, filtros, aliases, cursor pelo slug; limite máximo 48. Só projeções de publicações.
- `GET /entities/{slug}` — publicação atual; `?version=N` para histórico. `ETag` e `If-None-Match`.
- `GET /entities/{slug}/history` — até 100 revisões editoriais, mais recentes primeiro.
- `GET /entities/{slug}/diff?from_version=N&to_version=M` — diferenças de identificação, resumo e afirmações/evidências.
- `GET /featured` — seleção editorial de entidades existentes.
- `GET /sources` — metadados de fontes citadas em publicações; não expõe fontes privadas ainda não publicadas.
- `GET /timeline` — marcos reais selecionados, ordenados por data.
- `GET /stats` — contagens do corpus.

## Sessões
- `POST /auth/login` `{email,password}` — cookie seguro e token CSRF. Tentativas limitadas por email em janela de 15 minutos.
- `GET /auth/me` — utilizador e CSRF da sessão atual.
- `POST /auth/logout` — revoga a sessão.

Operações autenticadas que alteram estado exigem `X-CSRF-Token`.

## Redação
- `GET /editorial/drafts` — até 100 rascunhos recentes.
- `POST /editorial/drafts` — snapshot, afirmações, motivo e versão de base.
- `PUT /editorial/drafts/{id}?revision=N` — edição otimista; conflito devolve HTTP 409.
- `POST /editorial/drafts/{id}/submit` — submete um rascunho.
- `POST /editorial/drafts/{id}/review?approve=true|false` — editor/admin aprova ou devolve.
- `POST /editorial/drafts/{id}/publish` — publicação idempotente, exclusivamente editor/admin, apenas após aprovação.
- `GET|POST /editorial/sources` — fontes com autoria, URL e direitos obrigatórios.
- `GET /editorial/health` — fila, falhas, trabalho e publicações.

## Erros
401: sessão ausente/inválida. 403: permissões/CSRF/origem. 404: recurso ausente ou não publicado. 409: concorrência/estado incompatível. 422: contrato inválido. 429: limite de login.

## Limites conhecidos
REST interno de primeira versão; não é uma API pública licenciada. Não há quotas por cliente externo, contratos mobile estabilizados ou garantia de desempenho sob carga. Modelos detalhados de versões do jogo, geometrias e progresso sincronizado aguardam implementação.