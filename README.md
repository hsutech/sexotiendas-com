# sexotiendas.com

Sitio estático de [sexotiendas.com](https://sexotiendas.com), desplegado en Cloudflare.

## Estructura

- `index.html`: portada pública y estilos del sitio.
- `content/blog/`: artículo editorial firmado por Sofía.
- `assets/`: fotografía oficial autorizada y estilos editoriales.
- `site/`: salida estática generada para el Worker.
- `robots.txt`: reglas de rastreo.
- `sitemap.xml`: sitemap principal.
- `_redirects`: normalización del dominio `www`.

## Publicación

El repositorio contiene fuentes estáticas; el generador canónico de PBNS crea `site/` con portada, índice de blog y artículo. El Worker existente `sexotiendas` publica esa carpeta. No se crea otro Worker ni se cambian sus dominios.

- Rama de producción: `main`
- Directorio de salida: `site/`
- Dominio principal: `https://sexotiendas.com`

## Gestión

El repositorio está preparado para incorporarse al inventario y al flujo editorial de PBNS.

## SVibe top-ten batch — 2026-10-17

Approved articles are in their native content directories and `site/`. Rebuild the batch with canonical `pbns/work/publish-svibe-top10.py`, with the seven site repositories alongside the canonical checkout. That command preserves historical output outside the batch discovery pages. QA: canonical `work/check-svibe-top10.cjs` checks mobile/desktop rendering, images, links, TOC and canonical URLs. Evidence: canonical `outputs/svibe-top10-2026-10-17/`.

The 18 October 2026 style revision keeps the same nine-article campaign, original publication dates, product order and source links. Copy is edited section by section with one sentence per source line and at least 1,300 editorial words per article. Updated dates are visible and recorded in Article schema and sitemap. Review and QA: canonical `outputs/svibe-style-2026-10-18/`.


## SVibe comparison research revision — 18 October 2026

The existing top-ten articles now include individually researched product analysis, attributed external reviewer observations, price and specification tables, regional delivery caveats and official product photography. No hands-on testing is claimed. Canonical sources and research records live in `hsutech/pbns`, `content/svibe-top10-2026-10-17` and `outputs/svibe-deep-review-2026-10-18`.

## Article design — 18 October 2026

The SVibe top-ten routes use the `sexotiendas` editorial composition. Source configuration and portable, dependency-free enhancement live in `_article_design/`. Run `python3 _article_design/apply.py .` after generating HTML (native builders already invoke it). Navigation is keyboard-accessible, contents collapse on mobile, and all article prose and source links are preserved. Only configured article routes are enhanced; the historical catalogue stays unchanged. Canonical installer: `work/install-article-design.py`.

## First-person analysis and buyer opinions — 18 October 2026

The nine-article campaign was revised section by section for a conversational analytical voice. Named public buyer comments are attributed to their hosting store or Trustpilot; store verification labels are not independent purchase checks. No personal product testing, partner experience or editorial numerical score is claimed. The existing layouts, product photographs, comparison tables and URLs are preserved. Canonical evidence and independent review: `outputs/svibe-voice-2026-10-18/` in `hsutech/pbns`.

## SVibe product comparisons — 18 October 2026

New commissioned, research-based comparisons retain this site’s editorial layout. No firsthand testing or numerical editorial ratings are claimed. Official product imagery and attributed buyer observations accompany a two-product table.

- `content/blog/svibe-curve-vs-happy-rabbit-slimline-realistic.md` → https://sexotiendas.com/blog/svibe-curve-vs-happy-rabbit-slimline-realistic/
- `content/blog/svibe-jovi-vs-we-vibe-sync-2.md` → https://sexotiendas.com/blog/svibe-jovi-vs-we-vibe-sync-2/

Canonical research, independent review and publication receipts: `pbns/content/svibe-vs-2026-10-18/` and `pbns/outputs/svibe-vs-2026-10-18/`. Rebuild through the canonical batch integration script; the installed design pass supports `comparisonCount: 2` and scoped routes while preserving existing listicles.

## Related reading — 18 October 2026

The current product-comparison routes have three curated internal article links beneath their prose. `_article_design/config.json` stores each route’s `relatedArticles`; links remain inside this site and use the article language. The shared renderer leaves source prose and historical pages unchanged. Canonical metadata is in `content/svibe-vs-2026-10-18/manifest.json`; run `python3 work/install-related-articles.py svibe-vs-2026-10-18` from the canonical checkout to install/reapply this block. Normal batch regeneration preserves these selections.
