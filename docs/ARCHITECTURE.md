# VI Archive — decisões e limites da primeira fatia

Data: 2026-09-25. Estado: implementação inicial; não equivale à conclusão das fases 0–3.

## ADR 001: monólito modular e identidade

FastAPI com módulos de conhecimento, publicação, sessões e operação. MongoDB é a fonte de verdade. React 19 e TypeScript compõem a interface pública e a Redação. O frontend existente usa CRA/Craco e React Router em modo de biblioteca. **SSR e React Router em modo framework ainda não estão implementados** e permanecem requisito de fundação antes da fase pública orientada a SEO.

Os identificadores não mudam com uma revisão. O endereço de uma entidade já publicada é bloqueado nesta versão, evitando ligações partidas até implementar redirects/fusões. Novos tipos complexos, schemas tipados/unidades e configuração de relações ainda não são uma funcionalidade administrativa.

## ADR 002: publicação atómica sem replica set

O MongoDB fornecido executa em modo standalone e não aceita transações multi-documento. Não simulamos essa garantia.

1. As novas afirmações são gravadas como registos imutáveis, com identificadores determinísticos por rascunho e posição.
2. Uma única inserção em `publications` grava o snapshot editorial, referências às afirmações **e um evento de outbox incorporado**. Esta inserção de um documento é atómica em MongoDB standalone.
3. A existência dessa publicação — não a existência isolada de uma afirmação — determina visibilidade pública.
4. Um índice único `(entity_id, version)` impede duas publicações concorrentes na mesma versão.
5. `worker.py`, num processo supervisionado separado, atualiza a projeção `entity_search`. Há retries exponenciais e estado de falha após 8 tentativas.
6. As alterações à projeção são monotónicas: uma versão antiga nunca sobrescreve uma versão nova.
7. O único estado mutável da publicação é o processamento do evento em `outbox`. Snapshot, motivo e referências publicadas não são editáveis pelas APIs.

Falha antes de (2): podem sobrar afirmações órfãs, invisíveis ao público. Falha depois de (2): a publicação já é válida; o worker retoma o evento. Repetir a publicação é idempotente e reconcilia o estado do rascunho.

Este padrão substitui a transação multi-documento no ambiente atual. Uma transação real entre coleções requer MongoDB replica set e uma ADR de migração. Restauro, falhas injetadas e concorrência sob carga ainda precisam de exercícios formais.

## ADR 003: pesquisa inicial e suas limitações

`entity_search` é uma projeção reconstruível. Pesquisa por nome, aliases e texto normalizado; filtros por tipo/rótulo, paginação por cursor e limite máximo 48 por pedido. Tolerância a erros limitada a 200 candidatos quando não há correspondência. A ordenação estável usa slug.

Existe índice de texto ponderado para evolução. A recuperação atual utiliza regex literal escapada, não Atlas Search. **Não está validada para milhões de afirmações**. Atlas Search, analítica de lacunas, cursor opaco e monitorização p95 fazem parte da fase seguinte. O autocomplete apenas consulta a API pública; não lê rascunhos.

## ADR 004: evidência, corpus e materiais

12 entidades iniciais (5 personagens e 7 locais), 20 afirmações, todas com excerto de fonte oficial. `origin=oficial`, `nature=declaracao`, `verification=pendente`: não se inventa verificação humana ou observação em gameplay. Revisão inicial identificada como pendente, e não como um editor fictício.

Fontes consultadas a 25 de setembro de 2026:
- https://www.rockstargames.com/VI
- https://www.rockstargames.com/VI/only-in-leonida
- https://www.rockstargames.com/VI/media/screenshots

Imagens promocionais selecionadas da galeria oficial de downloads/partilha, com derivados WebP locais e atribuição. Não é declarada licença aberta; revisão jurídica/comercial continua pendente. Não são aceites uploads nem importações automáticas de URL. O registo manual de fonte guarda metadados, mas **não faz fetch do URL**, evitando SSRF nessa operação.

Os marcos da cronologia são seletivos, não uma lista completa. Não se publicam datas de lançamento voláteis como se estivessem congeladas no tempo. Mapa jogável, rankings, preços, armas e estatísticas não são fabricados.

## ADR 005: acesso e privacidade

Leitura pública; favoritos e checklist no localStorage, sem conta. Exportação JSON dos favoritos. Sem SDK de analytics incorporado pela aplicação.

Contas editoriais são provisionadas pelo administrador com `backend/manage.py`; não existe registo público ou promoção do primeiro visitante. Bcrypt, tokens de sessão opacos com hash em MongoDB, expiração em 8 horas, cookies Secure/HttpOnly/SameSite Strict, CSRF por sessão, verificação de origem e limites de tentativas de login. Permissões de publicação e revisão verificadas no servidor.

**Ainda pendente:** MFA, gestão de equipa, reset de palavra-passe, sessões por dispositivo, revisão obrigatória por outra pessoa em alterações sensíveis, limitação global de pedidos e consentimento para eventual analytics futuro. Estas ausências impedem qualificar a plataforma como operação editorial de produção completa.

## ADR 006: dois tempos e histórico

`recorded_at` e `created_at` representam o tempo de conhecimento/publicação no arquivo. `applicability` descreve o contexto conhecido do jogo. Não se adivinha uma versão, patch ou data de mudança do jogo. As versões numéricas públicas são **publicações editoriais**, não versões de GTA VI.

Histórico preservado, consulta `?version=N` e diferenças de campos/afirmações. Modelo relacional completo de `GameRelease`, intervalos bitemporais, fusões e ramos por plataforma/modo permanecem no backlog.

## Coleções

| Coleção | Autoridade / finalidade |
|---|---|
| entities | Identidade estável, slug reservado e tipo |
| assertions | Afirmações imutáveis e evidência contextual |
| sources | Metadados e direitos das fontes |
| publications | Publicação imutável e envelope de evento atómico |
| entity_search | Projeção reconstruível; não é a fonte de verdade |
| drafts | Trabalho editorial mutável com revisão otimista |
| users | Contas, hash de password, papel e estado |
| sessions | Tokens com hash, CSRF e TTL |
| audit_events | Ações editoriais com ator e data |
| timeline | Marcos reais documentados |
| login_attempts | Limite de tentativas, retenção por TTL de 15 minutos |

## Contratos

API `/api/v1`; documentação `/api/docs`, OpenAPI `/api/openapi.json`. Modelos de resposta excluem BSON `_id`. As fichas suportam ETags. Endpoints privados enviam `Cache-Control: no-store`. Os endpoints públicos não expõem rascunhos nem sessões.

## Operação

Processos: `frontend`, `backend`, `mongodb`, `archive-worker` sob supervisor. MONGO_URL e REACT_APP_BACKEND_URL originais preservados. O worker requer a configuração em `operations/archive-worker.conf` ao reproduzir o ambiente.

Não há ainda Object Storage, CDN gerida, OpenTelemetry, backups cifrados/restauro exercitado, alertas de filas ou testes de carga. Não é feita qualquer promessa de RPO/RTO, LCP ou p95 sem validação.