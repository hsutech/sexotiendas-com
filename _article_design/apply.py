#!/usr/bin/env python3
"""Dependency-free, scoped article layout pass; leaves editorial HTML intact."""
import hashlib
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
esc = html.escape
SCOPED_BATCH_SUPPORT = True
LABELS = {
    'en': dict(menu='Menu', nav='Main navigation', toc='In this guide', compare='Compare the 10 options', read='Read the guide', back='Explore the journal', top='Back to top', skip='Skip to content', updated='Updated', published='Published', legal='For adults 18+. Editorial information; not medical advice.', explore='Explore', about='About the journal', guide='Buying guide', more='Keep reading', moretext='More perspectives on intimate wellbeing, at your own pace.'),
    'es': dict(menu='Menú', nav='Navegación principal', toc='En esta guía', compare='Comparar las 10 opciones', read='Leer la guía', back='Explorar las guías', top='Volver arriba', skip='Saltar al contenido', updated='Actualizado', published='Publicado', legal='Para mayores de 18 años. Información editorial; no sustituye el consejo médico.', explore='Explorar', about='Sobre el sitio', guide='Guía de compra', more='Sigue explorando', moretext='Más lecturas sobre bienestar íntimo, a tu ritmo.'),
    'pt': dict(menu='Menu', nav='Navegação principal', toc='Nesta leitura', compare='Comparar as 10 opções', read='Ler o guia', back='Explorar o blog', top='Voltar ao início', skip='Pular para o conteúdo', updated='Atualizado', published='Publicado', legal='Para maiores de 18 anos. Informação editorial; não substitui orientação médica.', explore='Explorar', about='Sobre a publicação', guide='Guia de compra', more='A conversa continua', moretext='Mais leituras sobre bem-estar íntimo, no seu ritmo.'),
    'vi': dict(menu='Menu', nav='Điều hướng chính', toc='Trong bài viết', compare='So sánh 10 lựa chọn', read='Đọc bài viết', back='Xem các bài viết', top='Về đầu trang', skip='Chuyển đến nội dung', updated='Cập nhật', published='Đăng ngày', legal='Dành cho người từ 18 tuổi. Nội dung tham khảo, không thay thế tư vấn y tế.', explore='Khám phá', about='Thông tin', guide='Hướng dẫn chọn mua', more='Đọc thêm', moretext='Tìm hiểu thêm về sức khỏe thân mật theo cách phù hợp với bạn.'),
}

def link(label, href, active=False):
    if not href.startswith('/') or href.startswith('//'):
        raise ValueError('Chrome links must be internal')
    current = ' aria-current="location"' if active else ''
    return f'<a href="{esc(href, quote=True)}"{current}>{esc(label)}</a>'

def related_section(post, labels):
    """Render explicit, same-site recommendations without changing article prose."""
    titles = {'en': 'Related articles', 'es': 'Artículos relacionados', 'pt': 'Artigos relacionados', 'vi': 'Bài viết liên quan'}
    title = titles[post['language'][:2]]
    seen = {post['route']}
    cards = []
    entries = post['relatedArticles']
    if not 1 <= len(entries) <= 4:
        raise ValueError('Choose one to four related articles')
    for item in entries:
        route = item['route']
        link(item['title'], route)  # Apply the same internal-link policy as navigation.
        if route in seen:
            raise ValueError('Related links must be distinct and cannot link to this article')
        seen.add(route)
        description = f'<p>{esc(item["description"])}</p>' if item.get('description') else ''
        cards.append(f'<a class="j-related-card" href="{esc(route, quote=True)}"><h3>{esc(item["title"])}</h3>{description}</a>')
    return f'<section class="j-onward j-related" aria-labelledby="related-articles-bottom"><h2 id="related-articles-bottom">{title}</h2><nav class="j-related-grid" aria-label="{title}">{"".join(cards)}</nav><div class="j-related-back">{link(labels["back"], "/blog/")}</div></section>'

def meta(path):
    front = path.read_text().split('---\n', 2)[1]
    result = {}
    for line in front.strip().splitlines():
        key, value = line.split(':', 1)
        result[key] = value.strip().strip('"')
    return result

def extract(page):
    patterns = [r'<article class="j-copy"[^>]*>(.*?)</article>', r'<div class="wrap wrap--narrow post-body">(.*?)</div>\s*</article>', r'<article class="(?:op-prose|prose)">(.*?)</article>', r'<div class="layout">.*?<article>(.*?)</article>']
    body = None
    for pattern in patterns:
        found = re.search(pattern, page, re.S)
        if found:
            body = re.sub(r'<nav class="toc"[^>]*>.*?</nav>', '', found[1], flags=re.S)
            break
    if body is None:
        raise ValueError('Known article body missing')
    photo = re.search(r'<figure class="(?:j-hero-photo|article-photo wrap|editorial-figure|op-post-photo|product-photo)"[^>]*>(.*?)</figure>', page, re.S)
    if not photo:
        raise ValueError('Product hero missing')
    return body, photo[1]

def render(page, cfg, post, values, css, js):
    lang = post['language'][:2]
    t = dict(LABELS[lang])
    if post.get('comparisonCount') == 2:
        t['compare'] = {'en':'Compare both models','es':'Comparar los dos modelos','pt':'Comparar os dois modelos','vi':'So sánh hai mẫu'}[lang]
    t['compare'] = post.get('compareLabel', t['compare'])
    family = cfg['family']
    body, photo = extract(page)
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
    assert headings
    table_prefix = body.split('<div class="comparison-scroll"', 1)[0]
    table_anchor = re.findall(r'<h2 id="([^"]+)">', table_prefix)[-1]
    toc_items = ''.join(f'<li><a href="#{esc(i)}">{title}</a></li>' for i, title in headings)
    toc = f'<aside class="j-index"><details class="j-toc" open><summary>{t["toc"]}<span aria-hidden="true">＋</span></summary><nav aria-label="{t["toc"]}"><ol>{toc_items}</ol></nav></details></aside>'
    logo = cfg['logo']
    nav = ''.join(link(label, href, href == '/blog/') for label, href in cfg['nav'])
    header = f'<header class="j-header"><div class="j-masthead"><a class="j-brand" href="/" aria-label="{esc(cfg["brand"])}">{logo}</a><p class="j-tagline">{esc(cfg["tagline"])}</p><button class="j-toggle" type="button" aria-expanded="false" aria-controls="journal-menu">{t["menu"]}<span aria-hidden="true">＋</span></button><nav class="j-menu" id="journal-menu" aria-label="{t["nav"]}">{nav}</nav></div></header>'
    date = values['date']
    updated = values.get('updated', date)
    dates = f'<span>{t["published"]} <time datetime="{date}">{date.replace("-", ".")}</time></span><span class="article-updated">{t["updated"]} <time datetime="{updated}">{updated.replace("-", ".")}</time></span>'
    meta_html = f'<div class="j-byline"><span class="j-author">{esc(values["author"])}</span><div class="j-dates">{dates}</div></div>'
    actions = f'<div class="j-actions"><a class="j-cta" href="#{table_anchor}">{t["compare"]}<span aria-hidden="true">↘</span></a><a class="j-read" href="#article-body">{t["read"]} ↓</a></div>'
    title = f'<div class="j-intro"><p class="j-kicker">{t["guide"]} <span>· 18+</span></p><h1>{esc(values["title"])}</h1><p class="j-deck">{esc(values["description"])}</p>{meta_html}{actions}</div>'
    photo = f'<figure class="j-hero-photo">{photo}</figure>'
    # Deliberately different opening and reading compositions, not colour skins.
    if family == 'venus':
        hero = f'<section class="j-opening">{title}</section><div class="j-photo-strip">{photo}<p class="j-photo-note">{esc(cfg["photoNote"])}</p></div>'
    elif family == 'rab':
        hero = f'<section class="j-opening">{title}</section>'
    elif family == 'oficina':
        hero = f'<section class="j-opening">{photo}{title}</section>'
    elif family == 'cumen':
        hero = f'<section class="j-opening">{title}</section><div class="j-photo-strip">{photo}{toc}</div>'
    else:
        hero = f'<section class="j-opening">{title}{photo}</section>'
    if family == 'rab':
        reading = f'<div class="j-reading"><aside class="j-index j-reference">{photo}{toc.split(">", 1)[1].rsplit("</aside>", 1)[0]}</aside><article class="j-copy" id="article-body">{body}</article></div>'
    elif family == 'sexotiendas':
        reading = f'<div class="j-contents-band">{toc}</div><div class="j-reading"><article class="j-copy" id="article-body">{body}</article></div>'
    else:
        reading = f'<div class="j-reading">{toc if family != "cumen" else ""}<article class="j-copy" id="article-body">{body}</article></div>'
    related = ''.join(link(p['title'], p['route']) for p in cfg['posts'] if p['route'] != post['route'])
    related += link(t['back'], '/blog/')
    onward = f'<section class="j-onward"><div><p class="j-kicker">{esc(cfg["brand"])}</p><h2>{t["more"]}</h2><p>{t["moretext"]}</p></div><nav aria-label="{t["more"]}">{related}</nav></section>'
    if post.get('relatedArticles'):
        onward = related_section(post, t)
    main = f'<main class="j-main" id="main"><div class="j-container"><div class="j-breadcrumb">{link(cfg["blogLabel"], "/blog/")}<span aria-hidden="true">/</span><span>{t["guide"]}</span></div>{hero}{reading}{onward}</div></main>'
    footlinks = ''.join(link(label, href) for label, href in cfg['footer'])
    reading_links = ''.join(link(x['title'], x['route']) for x in cfg['posts'][-3:])
    reading_title = {'en':'Latest reading','es':'Últimas lecturas','pt':'Últimas leituras','vi':'Bài viết mới'}[lang]
    footer = f'<footer class="j-footer"><div class="j-footer-inner"><div class="j-footer-brand"><a class="j-brand" href="/">{logo}</a><p>{esc(cfg["footerText"])}</p></div><div class="j-footer-links"><h2>{t["explore"]}</h2><nav aria-label="{t["about"]}">{footlinks}</nav></div><div class="j-footer-reading"><h2>{reading_title}</h2><nav aria-label="{reading_title}">{reading_links}</nav></div><a class="j-top" href="#page-top">{t["top"]} ↑</a><div class="j-footer-bottom"><p>© 2026 {esc(cfg["brand"])}</p><p>{t["legal"]}</p></div></div></footer>'
    page = re.sub(r'<body([^>]*)>', '<body class="j-page j-'+family+'" id="page-top">', page, count=1)
    # Replace existing skip links with a single reliable destination.
    page = re.sub(r'<a class="(?:skip|op-skip|j-skip)"[^>]*>.*?</a>', '', page, flags=re.S)
    page = page.replace('id="page-top">', f'id="page-top"><a class="j-skip" href="#main">{t["skip"]}</a>', 1)
    page = re.sub(r'<header\b.*?</header>', lambda _: header, page, count=1, flags=re.S)
    page = re.sub(r'<main\b.*?</main>', lambda _: main, page, count=1, flags=re.S)
    page = re.sub(r'<footer\b.*?</footer>', lambda _: footer, page, count=1, flags=re.S)
    page = re.sub(r'<link[^>]*data-article-design[^>]*>|<script[^>]*data-article-design[^>]*></script>', '', page)
    page = page.replace('</head>', f'<link rel="stylesheet" href="/assets/{css}" data-article-design="2026-10-18"></head>')
    page = page.replace('</body>', f'<script src="/assets/{js}" defer data-article-design="2026-10-18"></script></body>')
    assert extract(page)[0] == body, 'Editorial HTML changed'
    return page

def apply(repo, config=None, selected_routes=None):
    if os.environ.get('ARTICLE_DESIGN_SKIP') == '1':
        return []
    cfg = config or json.loads((HERE/'config.json').read_text())
    assets = repo/'site/assets'
    assets.mkdir(parents=True, exist_ok=True)
    names = []
    for name in ['article.css', 'article.js']:
        data = (HERE/name).read_bytes()
        target = 'journal-design.'+hashlib.sha256(data).hexdigest()[:12]+Path(name).suffix
        (assets/target).write_bytes(data)
        names.append(target)
    results = []
    for post in cfg['posts']:
        if selected_routes is not None and post['route'] not in selected_routes:
            continue
        path = repo/'site'/post['route'].strip('/')/'index.html'
        if not path.exists():
            raise ValueError(f'Missing article: {path}')
        source = path.read_text()
        page = render(source, cfg, post, meta(repo/post['siteSource']), *names)
        path.write_text(page)
        results.append(str(path.relative_to(repo)))
    return results

if __name__ == '__main__':
    print(json.dumps(apply(Path(sys.argv[1]).resolve()), indent=2))
