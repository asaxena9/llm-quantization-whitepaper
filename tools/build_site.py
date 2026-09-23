#!/usr/bin/env python3
"""Build docs/index.html from paper/whitepaper.md.

Usage: python3 tools/build_site.py
Needs pandoc on PATH. The page loads Google Fonts when online and falls back to system fonts offline.
"""
import html
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / 'paper' / 'whitepaper.md'
OUT = ROOT / 'docs' / 'index.html'
REPO_URL = 'https://github.com/asaxena9/llm-quantization-whitepaper'
PDF_NAME = 'Aditya_Saxena_LLM_Quantization_Whitepaper_2025.pdf'

md = SRC.read_text(encoding='utf-8')
m = re.match(r'# (.+)\n', md)
title = m.group(1).strip()
rest = md[m.end():]
front, body = rest.split('\n## Introduction\n', 1)
body = '## Introduction\n' + body
body, refs_md = body.split('\n## References\n', 1)

lines = [l.rstrip() for l in front.strip().split('\n')]
byline = [re.sub(r'\*\*', '', l).rstrip('\\').strip() for l in lines if l and not l.startswith('>')]
author, affiliation, date = byline[0], byline[1], byline[2]
abstract = ' '.join(l[2:].strip() for l in lines if l.startswith('>'))
abstract = re.sub(r'^\*\*Abstract\.\*\*\s*', '', abstract)


def cite_group(match):
    nums = re.findall(r'\d+', match.group(0))
    links = ','.join(f'<a href="#src-{n}">{n}</a>' for n in nums)
    return f'<sup class="cite">{links}</sup>'


body_md = re.sub(r'(?:\[\d+\])+', cite_group, body)
res = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'html5', '--wrap=none'],
                     input=body_md, text=True, capture_output=True, check=True)
body_html = res.stdout
body_html = body_html.replace('<p>Table 1:', '<p class="caption">Table 1:')
body_html = body_html.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')

toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)
toc.append(('references', 'References'))
toc_html = '\n'.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)

refs = []
for line in refs_md.strip().split('\n'):
    mm = re.match(r'^(\d+)\. (?P<title>.+?) (?P<url>https?://\S+) \(cited as (?P<nums>[^)]+)\)\s*$', line)
    if not mm:
        continue
    nums = re.findall(r'\d+', mm.group('nums'))
    anchors = ''.join(f'<span id="src-{n}"></span>' for n in nums)
    cited = ', '.join(f'[{n}]' for n in nums)
    url = mm.group('url')
    refs.append(f'<li>{anchors}<a href="{html.escape(url)}">{html.escape(mm.group("title"))}</a>'
                f'<span class="url"><a href="{html.escape(url)}">{html.escape(url)}</a></span>'
                f'<span class="cited">Cited as {cited}</span></li>')
assert len(refs) == 10, len(refs)
refs_html = '\n'.join(refs)

CSS = """
:root{--ink:#1c1f24;--muted:#5a6270;--accent:#1f4e79;--accent-soft:#e9f0f7;--rule:#d9dde3;--paper:#ffffff;--bg:#f4f4f0;--code:#f0f1f3}
html{background:var(--bg)}
body{margin:0;color:var(--ink);font-family:"Source Serif 4",Charter,Georgia,"Times New Roman",serif;font-size:1.0625rem;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:46rem;margin:0 auto;padding:0 1.25rem}
.masthead{background:var(--paper);border-bottom:1px solid var(--rule);padding:3.5rem 0 2.25rem}
.eyebrow{font-family:Inter,system-ui,sans-serif;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 1rem;font-weight:600}
h1{font-family:"Source Serif 4",Charter,Georgia,serif;font-weight:600;font-size:clamp(1.7rem,4.2vw,2.5rem);line-height:1.18;margin:0 0 1.25rem;letter-spacing:-.01em}
.byline{font-family:Inter,system-ui,sans-serif;font-size:.95rem;color:var(--muted);margin:0 0 1.4rem;line-height:1.55}
.byline .author{color:var(--ink);font-weight:600;font-size:1.05rem}
.links a{font-family:Inter,system-ui,sans-serif;font-size:.85rem;font-weight:600;color:var(--accent);text-decoration:none;border:1px solid var(--accent);border-radius:999px;padding:.4rem .95rem;margin:0 .5rem .5rem 0;display:inline-block}
.links a:hover{background:var(--accent);color:#fff}
.sheet{background:var(--paper)}
.abstract{background:var(--accent-soft);border-radius:10px;padding:1.25rem 1.5rem;margin:2.25rem 0 2rem}
.abstract h2{font-family:Inter,system-ui,sans-serif;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin:0 0 .5rem}
.abstract p{margin:0;font-size:1rem}
.toc{margin:0 0 2.5rem;padding:0 0 1.5rem;border-bottom:1px solid var(--rule)}
.toc h2{font-family:Inter,system-ui,sans-serif;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 .6rem}
.toc ol{margin:0;padding-left:1.4rem;columns:2;column-gap:2rem;font-family:Inter,system-ui,sans-serif;font-size:.92rem;line-height:1.6}
.toc li{break-inside:avoid;margin:0 0 .25rem}
.toc a{color:var(--ink);text-decoration:none}
.toc a:hover{color:var(--accent);text-decoration:underline}
article.paper{counter-reset:sec}
article.paper h2{font-family:"Source Serif 4",Charter,Georgia,serif;font-weight:600;font-size:1.55rem;line-height:1.25;margin:2.75rem 0 1rem;letter-spacing:-.005em}
article.paper h2:not(.unnumbered){counter-increment:sec}
article.paper h2:not(.unnumbered)::before{content:counter(sec) ". ";color:var(--accent)}
article.paper p{margin:0 0 1.1rem}
article.paper ul,article.paper ol{padding-left:1.4rem;margin:0 0 1.2rem}
article.paper li{margin:0 0 .6rem}
strong{font-weight:600}
a{color:var(--accent)}
sup.cite{font-family:Inter,system-ui,sans-serif;font-size:.68em;line-height:0;vertical-align:baseline;position:relative;top:-.55em;margin-left:.08em}
sup.cite a{color:var(--accent);text-decoration:none}
sup.cite a:hover{text-decoration:underline}
.table-wrap{overflow-x:auto;margin:1.5rem 0 .75rem;border:1px solid var(--rule);border-radius:8px}
table{border-collapse:collapse;width:100%;font-family:Inter,system-ui,sans-serif;font-size:.84rem;line-height:1.45;min-width:680px}
thead th{background:var(--accent-soft);text-align:left;padding:.65rem .8rem;font-weight:600;border-bottom:1px solid var(--rule)}
tbody td{padding:.65rem .8rem;vertical-align:top;border-bottom:1px solid var(--rule)}
tbody tr:last-child td{border-bottom:none}
tbody tr:nth-child(even) td{background:#fafaf8}
p.caption{font-family:Inter,system-ui,sans-serif;font-size:.85rem;color:var(--muted);line-height:1.5;margin:0 0 1.75rem}
code{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:.88em;background:var(--code);padding:.1em .3em;border-radius:4px}
.refnote{font-family:Inter,system-ui,sans-serif;font-size:.9rem;color:var(--muted)}
ol.refs{padding-left:1.6rem;font-family:Inter,system-ui,sans-serif;font-size:.92rem;line-height:1.55}
ol.refs li{margin:0 0 .9rem}
ol.refs .url{display:block;font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:.76rem;word-break:break-all}
ol.refs .url a{color:var(--muted);text-decoration:none}
ol.refs .url a:hover{text-decoration:underline}
ol.refs .cited{display:block;font-size:.8rem;color:var(--muted)}
footer{padding:2rem 0 3rem;font-family:Inter,system-ui,sans-serif;font-size:.85rem;color:var(--muted)}
footer a{color:var(--accent)}
@media (max-width:640px){.toc ol{columns:1}body{font-size:1rem}.masthead{padding:2.5rem 0 1.75rem}.abstract{padding:1rem 1.1rem}}
@media print{
@page{size:Letter;margin:0.85in 0.9in}
html,body{background:#fff}
body{font-size:10.5pt;line-height:1.55;color:#000}
.wrap{max-width:none;padding:0}
.masthead{padding:0 0 1rem;border-bottom:1px solid #999}
.links{display:none}
h1{font-size:22pt}
article.paper h2{font-size:14pt;margin:1.6rem 0 .6rem;page-break-after:avoid;break-after:avoid}
.abstract{background:#f2f2f2;-webkit-print-color-adjust:exact;print-color-adjust:exact;margin:1.5rem 0}
.toc{break-inside:avoid;page-break-inside:avoid;margin:0 0 1.5rem;padding:0 0 1rem}
.toc h2{break-after:avoid;page-break-after:avoid}
.table-wrap{overflow:visible;border:none;margin:1rem 0 .4rem}
table{min-width:0;font-size:8pt;line-height:1.35}
tr{page-break-inside:avoid;break-inside:avoid}
thead{display:table-header-group}
thead th,tbody td{padding:.4rem .5rem}
thead th{background:#e8e8e8;-webkit-print-color-adjust:exact;print-color-adjust:exact}
tbody tr:nth-child(even) td{background:#f6f6f6;-webkit-print-color-adjust:exact;print-color-adjust:exact}
a{color:#000;text-decoration:none}
sup.cite a{color:#1f4e79}
ol.refs .url a{color:#444}
ol.refs .url{font-size:7.5pt}
footer{display:none}
p,li{orphans:3;widows:3}
}
"""

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(abstract[:200])}">
<meta name="author" content="{html.escape(author)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400;1,8..60,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <p class="eyebrow">White paper &middot; {html.escape(date)}</p>
    <h1>{html.escape(title)}</h1>
    <p class="byline"><span class="author">{html.escape(author)}</span><br>{html.escape(affiliation)}</p>
    <p class="links"><a href="{PDF_NAME}">Download the PDF</a><a href="{REPO_URL}">Source on GitHub</a></p>
  </div>
</header>
<div class="sheet">
<main class="wrap">
  <section class="abstract"><h2>Abstract</h2><p>{html.escape(abstract)}</p></section>
  <nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>
{toc_html}
  </ol></nav>
  <article class="paper">
{body_html}
<h2 id="references" class="unnumbered">References</h2>
<p class="refnote">Numbers in square brackets in the text point to the sources below. The citation numbers follow the original draft, so several numbers can point to the same source.</p>
<ol class="refs">
{refs_html}
</ol>
  </article>
</main>
</div>
<footer class="wrap">
  <p>{html.escape(author)}, {html.escape(date)}. Source, Markdown and PDF: <a href="{REPO_URL}">{REPO_URL.replace('https://', '')}</a></p>
</footer>
</body>
</html>
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(page, encoding='utf-8')
print(f'wrote {OUT} ({len(page):,} bytes); sections: {len(toc)}; references: {len(refs)}')
