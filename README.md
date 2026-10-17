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
