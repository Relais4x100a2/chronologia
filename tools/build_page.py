"""Regénère la page HTML de l'étude à partir du document Markdown.

Usage : python3 tools/build_page.py
Entrée : docs/modele-evenement-masque-factoide.md
Sortie : docs/etude-page-claude.html (page publiée sur claude.ai, sans balises html/head/body)
Dépendance : pip install markdown
"""
import re
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parent.parent
md = (ROOT / "docs/modele-evenement-masque-factoide.md").read_text(encoding="utf-8")
head = (ROOT / "tools/page_head.html").read_text(encoding="utf-8")

body = markdown.markdown(
    md,
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
    extension_configs={"toc": {"slugify": slugify_unicode}},
)
body = re.sub(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>',
    lambda m: '<div class="diagram"><pre class="mermaid">' + m.group(1) + "</pre></div>"
    '<p class="note">Sur mobile, faites défiler le diagramme horizontalement.</p>',
    body,
    flags=re.S,
)
body = body.replace("<pre><code", '<pre class="code"><code')
body = re.sub(r"<table>(.*?)</table>", r'<div class="tbl"><table>\1</table></div>', body, flags=re.S)
# Le sommaire suit la convention GitHub ; on recale ses liens sur les ancres générées.
for anchor, num in re.findall(r'<h2 id="([^"]+)">(\d+)\.', body):
    body = re.sub(r'href="#%s-[^"]*"' % num, 'href="#%s"' % anchor, body, count=1)

(ROOT / "docs/etude-page-claude.html").write_text(head + '<main class="doc">\n' + body + "\n</main>\n", encoding="utf-8")
print("Page régénérée : docs/etude-page-claude.html")
