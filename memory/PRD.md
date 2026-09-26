# VI Archive — Product Requirements & Delivery Record

## Pedido original e visão (requisitos estáticos)

**«Plataforma mundial de conhecimento sobre GTA 6 — Arquitetura de fundação — versão 1»**

Pedido original: aplicação web responsiva, API preparada para futuros clientes mobile e integrações. A visão substitui LobbyReady. O produto combina arquivo, base de dados, publicação editorial e ferramentas de jogo sobre **um único núcleo de conhecimento**.

Princípio do utilizador: **«documentar tudo é uma direção, não um requisito para lançar»**. Confiança depende de evidências, revisão e capacidade editorial, não da dimensão da infraestrutura.

Percurso principal: **pergunta → resultado útil → informação contextualizada e evidenciada → mapa, comparação ou guia → guardar opcionalmente**.

Princípio final original: **«o ativo principal não será o volume de artigos. Será um conjunto de conhecimento estruturado, rastreável e preservado, que pode alimentar muitas ferramentas sem deixar de explicar de onde veio cada informação.»**

### As 15 áreas do documento original

1. Produto: Explorar (entidades/relações), Encontrar (pesquisa/filtros/mapa), Resolver (guias/comparadores/checklists), Acompanhar (notícias/alterações) e Guardar (favoritos/progresso). Sexta área privada: Redação.
2. Stack obrigatório: React + TypeScript, FastAPI, MongoDB. Monólito modular, React Router framework com SSR/pré-render, Atlas Search reconstruível, Object Storage/CDN, workers separados e OpenTelemetry. Publicação + outbox atómicas.
3. Modelo: Entity, EntityType/Schema, Assertion, Source/Evidence, GameRelease, Document, Revision/Publication, Map/SpatialFeature, User/Collection/Progress, EditorialTask/AuditEvent. Relações são afirmações; conhecimento publicado canónico é a autoridade.
4. Extensibilidade: famílias de personagens/organizações, equipamentos, mundo, conteúdo jogável, sistemas, cultura/narrativa e evolução. Schema disponível não prova que conteúdo existe.
5. Evidência: origem, natureza, verificação e aplicabilidade separadas. Confiança por afirmação, com fonte, excerto/localização, consulta, método e revisão. Conservar contradições; rumores separados; desconhecido nunca convertido em zero.
6. Preservação: distinguir tempo do jogo de tempo do arquivo, versões identificadas por ramos/plataformas/modos, histórico/diffs, IDs estáveis, redirects/fusões e revisões publicadas imutáveis.
7. Redação: submissão, triagem, investigação, revisão, publicação, monitorização. RBAC com seis papéis, revisão adicional de alterações sensíveis, importações validadas, deduplicação, conflitos, auditoria e saúde do arquivo. Automação nunca publica factos por si.
8. Encontrar: aliases, sinónimos, erros ortográficos, autocomplete, filtros, campos ponderados. Comparadores com unidades/contextos compatíveis e sem rumores por defeito. Cursor, índices, limites; validar desempenho sem promessas não demonstradas.
9. Mapa/guias/notícias/cronologias: Leaflet com coordenadas verificáveis e legais; não fabricar mapa ou trajetos. Documentos ligados a entidades; separar cronologia ficcional da história real; proteger spoilers.
10. Contas/progresso/analytics: leitura sem conta, favoritos locais, sincronização opcional, perfis de jogo. Sem promessa de integração Rockstar não autorizada. Analytics minimizados, consentimento e retenção; procura gera tarefas, nunca factos.
11. Design e SEO: identidade independente, premium, mobile-first; pesquisa acessível, teclado, WCAG 2.2 AA como objetivo. Ordem: resposta → essenciais → fontes/contexto → detalhe → relações. HTML público renderizado, canonical, sitemap, redirects, metadata e política noindex.
12. Segurança/operação: RBAC, MFA, sessões, CSRF/XSS, uploads isolados, SSRF, limites, cache sem dados privados, backups cifrados/restauro, logs/traces/métricas. Metas LCP/p95 só após validação.
13. API/manutenção: REST versionada, OpenAPI, cursores, ETags, contratos públicos/editoriais separados, licenças/quotas antes de API pública; ADRs, dicionário de dados, migrações e runbooks.
14. Fases: 0 contratos; 1 fatia entidade→afirmação→evidência→revisão→publicação→pesquisa→histórico; 2 produto público pré-lançamento; 3 operação de lançamento; crescimento posterior por utilidade. Critério da fase 1 inclui propagação, permissões, falhas e restauro.
15. Decisões abertas: nome/domínio, idioma, equipa, orçamento, negócio, direitos e moderação. Não escolher anúncios/subscrições ou financiar estatuto de verificado.

## Decisões de interação com o utilizador

- Utilizador pediu início imediato e dispensou esclarecimentos: «No need for clarification, just proceed with your best judgment.»
- Defaults assumidos: nome provisório **VI Archive**, interface português europeu, poucas entidades oficiais, acesso editorial privado por email/palavra-passe, favoritos locais.
- Preferência de trabalho posterior: «Continua sem testes». Não foi efetuada uma regressão abrangente.
- Depois reportou erro real de compilação em `ArchiveSearch.tsx` e pediu explicitamente verificação pelo testing_agent. Essa verificação foi limitada à compilação e pesquisa afetadas.

## Personas

- Jogador casual: encontrar uma pessoa/local e obter uma resposta clara.
- Investigador/criador/jornalista: chegar à evidência e distinguir declaração de verificação.
- Colaborador: propor conteúdo sem poder alterar diretamente a publicação.
- Editor/administrador: rever, publicar, preservar histórico e acompanhar estado da fila.
- Speedrunner e jogador avançado: futuros contextos de versão, medições e ferramentas, ainda não implementados.

## Arquitetura implementada

- Frontend React 19 + TypeScript, React Router **em modo biblioteca** sobre CRA/Craco existente. Shadcn/Radix para controlos, drawer e confirmações; lucide e sonner. Visual dark Vice Night, rosa/ciano, Unbounded/IBM Plex Sans/JetBrains Mono.
- Backend modular FastAPI: `core.py`, `models.py`, `auth.py`, `knowledge.py`, `editorial.py`, `seed.py`, `worker.py`.
- MongoDB com identidades, afirmações, fontes, publicações, projeção, rascunhos, sessões, utilizadores, audit_events e cronologia.
- Standalone Mongo não permite transações multi-documento: publicação e outbox incorporado são gravados num único envelope atómico; afirmações preparadas ficam invisíveis sem publicação. Snapshot/afirmações imutáveis, índice único entidade+versão, worker independente idempotente, retries/falhas e projeção monotónica.
- Sessões opacas com cookie Secure/HttpOnly/SameSite Strict, CSRF, RBAC, bcrypt, TTL e limite de login. Contas só por comando administrativo privado; sem promoção pública.
- URLs de API e Mongo vêm das configurações originais, preservadas. Servidores sob supervisor; worker em processo separado.
- Imagens promocionais selecionadas da galeria Rockstar com atribuição e derivados WebP locais. Não há uploads nem armazenamento externo nesta entrega.
- Decisões e limitações detalhadas: `/app/docs/ARCHITECTURE.md`. Contratos: `/app/docs/API.md`.

## Implementado — 2026-09-25

### Experiência pública
- Início diretamente no arquivo, com pesquisa, categorias, destaques e navegação das cinco áreas.
- Corpus inicial: 12 entidades, 20 afirmações (5 personagens, 7 locais); fontes oficiais consultadas; nenhum dado de jogo fictício.
- Pesquisa com aliases/texto normalizado, correspondência aproximada limitada, filtros, cursores, vista de lista/grelha e autocomplete de cabeçalho.
- Fichas com dimensões de evidência, painel de fonte/excerto/método/consulta/revisor, ligações bidirecionais e controlo de spoiler nos campos assinalados.
- Histórico editorial, publicação anterior e endpoint/UI de diferenças de identificação, resumo e afirmações.
- Favoritos locais persistentes, exportação JSON, remoção/limpeza confirmada. Pedidos por lotes para conjuntos maiores de guardados.
- Checklist local de leitura, cronologia de marcos reais selecionados, metodologia e direitos.
- Estados honestos de ausência de evidência para mapas, estatísticas e comparadores. Não são simulações de ferramentas operacionais.

### Redação
- Login/logout protegido; conta inicial de administrador `editor@viarchive.pt` provisionada privadamente. Password não armazenada neste documento.
- Criação/edição de rascunhos com fonte e excerto obrigatórios, nomes/aliases, natureza/origem/verificação/aplicabilidade e motivo.
- Proposta de revisão de entidade existente, controlo otimista de conflitos, submissão, inspeção, aprovação/devolução e publicação com permissões no servidor.
- Registo manual de fontes com autoria, URL e direitos; sem fetch de URLs arbitrários.
- Auditoria persistente e indicadores de fila/falhas/publicações.
- Repetição de publicação reconcilia o estado do rascunho se a resposta original falhar após o commit.

### Correção reportada — 2026-09-25
- Erro: Babel `Unexpected token, expected "}" (20:816)` e TS1005 em `ArchiveSearch.tsx`.
- Causa: fecho incompleto do atributo JSX com `onKeyDown` inline.
- Alteração: extrair `handleKeyDown` tipado, JSX multiline legível, cancelar pesquisas antigas, limpar seleção anterior e evitar seleção de resultados em carregamento.
- **Verificação dirigida pelo testing_agent**: `/app/test_reports/iteration_1.json`; `yarn tsc --noEmit` e `yarn build` aprovados; página sem overlay, clique em Jason, setas/Escape/Enter para Lucia e envio sem seleção aprovados.
- Detalhe menor do relatório: popup de autocomplete ultrapassava a margem esquerda móvel em aproximadamente 2 px. Corrigido com alinhamento fixo entre margens de 15 px em ecrãs até 760 px.
- Esta verificação não certifica as restantes áreas, a segurança, a carga ou os critérios completos da fase 1.

## Estado da entrega

Primeira implementação funcional, não conclusão da arquitetura de uma década nem passagem formal da fase 1. O critério de falhas/restauro ainda não foi demonstrado. Não afirmar que SSR, Atlas Search, MFA, Object Storage, CDN ou OpenTelemetry estão integrados.

## Backlog priorizado

### P0 — fundação antes de operação pública completa
1. React Router framework com SSR e pré-render seletivo, metadata por entidade e dados estruturados.
2. MFA editorial, revisão independente obrigatória para alterações sensíveis, gestão de contas e recuperação/rotação de palavra-passe.
3. Exercícios de falha/replay/restauro, backups cifrados separados e metas RPO/RTO acordadas.
4. Formalizar direitos, política editorial e revisão humana do corpus inicial, mantendo `verification=pendente` até haver fundamento.
5. Verificar o percurso editorial end-to-end em ambiente de testes isolado; não publicar fixtures no corpus real.
6. Schemas de campos tipados/unidades/validações e relações permitidas; fechar contratos de aplicabilidade e GameRelease.

### P1 — produto público e qualidade
1. Atlas Search (ainda não provisionado), ranking ponderado/aliases/sinónimos, autocomplete ordenado por relevância; substituir recuperação regex limitada.
2. Canonical SSR, sitemaps segmentados, redirects/fusões e política de histórico/noindex completa.
3. Documentos estruturados para notícias e guias, referências vivas a afirmações e pendências de revisão.
4. Fila comunitária de correções/descobertas e permissões por área; UI de auditoria, retries manuais e saúde de fontes.
5. OpenTelemetry, alertas, medidas de latência e indexação, limites globais/bots e cache por contexto.
6. Object Storage/CDN quando forem aceites uploads e materiais com direitos confirmados.
7. Históricos/diffs bitemporais, releases por plataforma/modo e contexto histórico das relações.
8. Auditoria de acessibilidade, contraste e desempenho mobile; nenhuma certificação WCAG/LCP/p95 alegada.

### P2 — após dados verificados e capacidade editorial
1. Leaflet com mapas/geometrias legalmente utilizáveis e confirmados; rede validada antes de rotas.
2. Comparadores e guias de jogo com medições compatíveis e campos conhecidos; não inventar valores.
3. Contas opcionais, sincronização de coleções e perfis de progresso, sem prometer saves Rockstar.
4. Listas partilháveis de descobertas com fontes preservadas.
5. Internacionalização editorial, analytics consentidos/minimizados e agrupamento de pesquisas sem resposta.
6. Importações/deduplicação auditadas, automação assistiva sem publicação autónoma, API externa licenciada/quota.

## Android offline — pedido confirmado

- Utilizador escolheu APK sem URL HTTPS, totalmente offline (opção A) e assinatura permanente (opção B).
- Implementado exportador read-only do corpus oficial versionado em `backend/seed.py`: 12 entidades, 20 afirmações, fontes/evidências/relações/histórico inicial e cronologia. Não exporta dados de um servidor nem inventa conteúdo.
- `yarn build:offline` gera bundle separado com fontes locais/licenças e imagens. `REACT_APP_OFFLINE=true` seleciona consultas locais compatíveis com a API pública; website online mantém configuração existente. Nenhuma alteração no backend ou nos `.env`.
- Login/redação indisponíveis explicitamente no APK. Favoritos/checklist locais mantidos; exportação JSON preparada para seletor nativo. Ligações externas precisam de Internet fora da aplicação.
- Projeto Java Android em `android/`: WebViewAssetLoader local, bloqueio de rede, sem permissão INTERNET, navegação voltar, insets, exportação restrita. AGP8.9.1/Gradle8.11.1/JDK17/SDK35/WebKit1.12.1, pacote `pt.viarchive.app`.
- Workflow `.github/workflows/android-apk.yml`: cada push/dispatch compila e verifica release com chave permanente vinda de quatro GitHub Secrets; sem chave efémera/fallback debug. APK/checksum/certificado/versão em artefactos. Segredos e execução GitHub ainda não configurados pelo proprietário.
- `docs/ANDROID.md` explica criação única/backup da chave, configuração, downloads e atualizações. Sem publicação Play Store ou instalação automática.
- Verificado até agora: exportação do corpus, TypeScript, lint dos ficheiros alterados e build offline bem-sucedidos. Build Android e testes delegados em curso; testes UI dependem de autorização. Ambiente de fork sem `.env`; não restaurar URLs por suposição. Apenas `/app` persiste entre recriações, usar `.cache` para toolchains.

## Próximas ações sugeridas

1. Confirmar identidade/idioma e nomear responsáveis editoriais.
2. Fechar os P0 de renderização pública, acesso e recuperação do arquivo.
3. Rever o corpus inicial e aprofundar uma categoria com evidências, não apenas mais páginas.
