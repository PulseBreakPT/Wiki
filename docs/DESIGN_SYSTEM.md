# VI Archive — edição visual 02

Data: 2026-09-25.

## Pedido e preferências

Pedido: «Melhora significativamente o design do site para o SSS tier».

O utilizador escolheu combinar direção cinematográfica editorial, arquivo premium e liberdade de reinvenção; manter **VI Archive, rosa/ciano e fundo escuro**. Preferência adicional literal: «Usa mais cores da UI e HUD do gta 6».

Interpretação: linguagem visual inspirada nas cores e nos materiais promocionais oficiais, sem alegar reprodução de um HUD confirmado ou acessível. A arquitetura editorial continua independente da Rockstar Games.

## Identidade

- Rosa Vice: `#FF82B2`, Explorar, identidade e ações primárias.
- Ciano: `#79E4ED`, Encontrar, fontes, relações e foco de teclado.
- Verde menta: `#A3E3BD`, Resolver, origem oficial e progresso.
- Dourado solar: `#F6CB80`, Acompanhar, contexto e estados pendentes.
- Lilás: `#C1B2F2`, Guardar e estados editoriais.
- Base carvão `#0E1015`, superfícies `#17191F`, texto `#F5F3F5`.

Display Unbounded; corpo IBM Plex Sans; rótulos e referências JetBrains Mono. Texto principal 13–15 px, títulos de ficha 32–49 px, hero até 50 px. Mantêm-se rótulos auxiliares mais pequenos para metadados não essenciais.

## Composição

- Sidebar refinada com cores semânticas, estados ativos e identidade independente.
- Pesquisa persistente com combobox funcional e sugestões ligadas ao arquivo.
- Hero full-bleed com arte oficial Jason and Lucia 01, título curto, pesquisa real e atribuição.
- Categorias com acentos por tipo, dossiês com imagens de proporção estável, resumos e afirmações reais.
- Secção panorâmica Leonida Keys e índice visual de outros locais existentes.
- Fichas, pesquisa, cronologia, checklist, metodologia, guardados e Redação partilham escala, cores e espaçamento.
- Drawer de evidência com dimensões separadas, excerto destacado e textos legíveis.
- Animação inicial e entrada dos dossiês com Framer Motion. Hover discreto. Respeito por `prefers-reduced-motion`.

## Mobile

- Navegação inferior fixa com cinco áreas até 900 px.
- Menu secundário lateral com botão de fecho, Escape e bloqueio de scroll do corpo.
- Autocomplete encaixado dentro das margens do ecrã.
- Fichas de dossiê numa coluna até 430 px, mantendo texto e ações utilizáveis.
- Formulários, tabelas editoriais e afirmações refluem sem depender de scroll horizontal.
- Safe area inferior contemplada na navegação móvel.

## Assets e direitos

Imagem principal: `Jason_and_Lucia_01_landscape.12x2gvspcm_3m.jpg`, selecionada na galeria oficial:
https://www.rockstargames.com/VI/downloads/artwork-wallpapers

Imagens de entidades e Leonida Keys mantêm as origens oficiais já documentadas em `ARCHITECTURE.md`. O script `scripts/prepare_media.py` documenta os URLs dos derivados locais WebP. Direitos continuam com os titulares; não é declarada licença aberta ou afiliação.

## Implementação

`src/App.css` é o ponto de entrada, dividido em:
- `styles/shell.css`: tokens, layout, navegação, pesquisa global e utilitários.
- `styles/explore.css`: hero, categorias, dossiês e secções editoriais.
- `styles/content.css`: pesquisa, entidades, evidência, guardados, checklist, cronologia e metodologia.
- `styles/editorial.css`: acesso e trabalho editorial.
- `styles/responsive.css`: adaptações por breakpoint e movimento reduzido.

A antiga cascata de overrides em `refinements.css` foi removida. Contratos API, persistência, autenticação e regras editoriais não foram alterados nesta intervenção visual.