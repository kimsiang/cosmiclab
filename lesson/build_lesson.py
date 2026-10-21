"""Build the sample lesson as a Colab notebook and as an in-browser page.

    python build_lesson.py      # needs: pip install markdown
Writes lesson/sample-lesson.ipynb and ../sample-lesson.html from lesson_cells.py.
"""
import json, html, os, textwrap
import markdown
from lesson_cells import TITLE, SUB, CELLS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "kimsiang/cosmiclab"
COLAB = f"https://colab.research.google.com/github/{REPO}/blob/main/lesson/sample-lesson.ipynb"

def clean(s): return textwrap.dedent(s).strip("\n")

# ── notebook ──
nb_cells = [{"cell_type": "markdown", "metadata": {}, "source":
    [f"# Cosmic Lab · Sample lesson: {TITLE}\n", "\n", f"{SUB}\n"]}]
for kind, src in CELLS:
    lines = clean(src).splitlines(keepends=True)
    if kind == "md":
        nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": lines})
    else:
        nb_cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                         "outputs": [], "source": lines})
nb = {"nbformat": 4, "nbformat_minor": 5, "cells": nb_cells,
      "metadata": {"colab": {"name": "Cosmic Lab sample lesson", "provenance": []},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"}}}
with open(os.path.join(HERE, "sample-lesson.ipynb"), "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

# ── web page ──
blocks, n = [], 0
for kind, src in CELLS:
    if kind == "md":
        blocks.append(f'<div class="prose">{markdown.markdown(clean(src))}</div>')
    else:
        n += 1
        code = html.escape(clean(src))
        blocks.append(f'''<div class="cell" data-n="{n}">
  <div class="cell-bar"><span class="cell-n">In [{n}]</span>
    <button class="reset" type="button" title="Restore the original code">Reset</button>
    <button class="run" type="button"><span>Run</span></button></div>
  <div class="ed"><pre class="hl" aria-hidden="true"></pre><textarea spellcheck="false" autocapitalize="off" autocomplete="off" aria-label="Python code, cell {n}">{code}</textarea></div>
  <div class="out" aria-live="polite"></div>
</div>''')

tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
page = (tpl.replace("{{TITLE}}", html.escape(TITLE)).replace("{{SUB}}", html.escape(SUB))
           .replace("{{COLAB}}", COLAB).replace("{{CELLS}}", "\n".join(blocks)))
with open(os.path.join(HERE, "..", "sample-lesson.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("built", n, "code cells")
