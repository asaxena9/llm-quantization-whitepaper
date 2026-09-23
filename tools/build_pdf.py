#!/usr/bin/env python3
"""Render docs/index.html to a PDF with Chrome and set the PDF metadata.

Usage: python3 tools/build_site.py && python3 tools/build_pdf.py
Needs Google Chrome (or Chromium) and the pypdf package.
"""
import pathlib
import re
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / 'docs' / 'index.html'
OUT = ROOT / 'docs' / 'Aditya_Saxena_LLM_Quantization_Whitepaper_2025.pdf'
CANDIDATES = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')]
chrome = next(p for p in CANDIDATES if p and pathlib.Path(p).exists())
subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                '--virtual-time-budget=15000', f'--print-to-pdf={OUT}', INDEX.as_uri()],
               check=True, capture_output=True)

from pypdf import PdfReader, PdfWriter  # noqa: E402

title = re.match(r'# (.+)', (ROOT / 'paper' / 'whitepaper.md').read_text(encoding='utf-8')).group(1).strip()
reader = PdfReader(str(OUT))
writer = PdfWriter()
writer.append(reader)
writer.add_metadata({
    '/Title': title,
    '/Author': 'Aditya Saxena',
    '/Subject': 'White paper on post-training quantization methods for large language models and vision-language models, 2023 to 2025',
    '/Keywords': 'quantization, LLM, VLM, GPTQ, AWQ, OWQ, SpQR, SqueezeLLM, SmoothQuant, Atom, INT8, INT4, edge AI',
    '/Creator': 'tools/build_pdf.py',
    '/Producer': 'Chrome print to PDF, metadata by pypdf',
})
with open(OUT, 'wb') as fh:
    writer.write(fh)
print(f'wrote {OUT} ({OUT.stat().st_size:,} bytes, {len(reader.pages)} pages)')
