---
name: bc-pdf-reading
description: Read, inspect, and pull content out of PDF files on disk — text, tables, embedded images, attachments, and form field values. Use this whenever a task involves opening or understanding a .pdf that isn't already in context, or on requests like "read this PDF", "summarize the report at ./doc.pdf", "pull the tables out of this PDF", "what does page 4 look like", "extract the images from this PDF", "what are the form field values in this PDF", or any time a .pdf path is mentioned and its contents matter to the task. Fallback for environments without a first-party PDF-reading skill already installed. Does not cover creating, merging, splitting, watermarking, or encrypting PDFs.
---

# Reading PDFs

The core problem with PDFs: a page can be real text, a scanned photo of
text, a vector drawing, or some mix of all three — and you can't tell
which until you look. Don't guess. Triage first, then pick the right
extraction method per page.

## Step 1 — Triage before extracting anything

```bash
pdfinfo target.pdf          # page count, size, PDF version, metadata
pdffonts target.pdf         # is there an actual text layer?
```

Read the `pdffonts` output first:

- **No rows at all** → there is no text layer. The page is a scanned
  image. `pdftotext` will silently return nothing. Skip straight to
  "Scanned pages" below.
- **Rows present, but `Emb` column says `no`** → fonts aren't embedded
  and may use a custom encoding. Extraction can come out as garbage
  characters. Treat any extracted text from these fonts with suspicion
  and cross-check visually if it matters.
- **Rows present with `Emb = yes`** → normal case, extraction should
  be clean. Proceed to Step 2.

If figures, embedded files, or forms might matter, also run:

```bash
pdfimages -list target.pdf     # raster images present?
pdfdetach -list target.pdf     # embedded files present?
pdftk target.pdf dump_data_fields   # form fields present?
```

## Step 2 — Get the text

Three tools, different strengths:

| Tool | Best for |
|---|---|
| `pdftotext -layout target.pdf out.txt` | Fast, preserves column/table spacing reasonably well |
| `pypdf` | Simple per-page extraction in a Python pipeline |
| `pdfplumber` | When you also need bounding boxes or real table extraction |

```python
# pypdf — quick and simple
from pypdf import PdfReader
reader = PdfReader("target.pdf")
pages_text = [p.extract_text() or "" for p in reader.pages]
```

```python
# pdfplumber — when tables matter
import pdfplumber
with pdfplumber.open("target.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        tables = page.extract_tables()   # list of list-of-rows
```

If `pdftotext` output looks scrambled (words out of order, weird
spacing) but `pdfplumber`'s does not, prefer `pdfplumber` — it's
layout-aware where `pdftotext` in non-layout mode is not.

## Step 3 — When text alone isn't enough, look at the page

Text extraction is blind to charts, diagrams, equations, and anything
communicated visually rather than textually. When that matters,
rasterize the specific page and view it as an image rather than
guessing from surrounding text:

```bash
pdftoppm -jpeg -r 150 -f 4 -l 4 target.pdf /tmp/pg
# output filename is zero-padded to match the page count —
# check what actually got written before assuming a name:
ls /tmp/pg-*
```

150 DPI is a good default — enough to read labels and axis text
without generating an enormous file. Only rasterize the pages you
actually need; doing this for every page of a long document burns a
lot of tokens for little benefit on text-heavy pages.

**Rule of thumb for which path to take:**

- Narrative text, reports, contracts → text extraction, done.
- Charts, scanned figures, hand-marked diagrams → rasterize that page.
- Tables → try `pdfplumber.extract_tables()` first; rasterize only if
  the table structure comes out broken.
- High-stakes precision (financial figures, legal language) → do
  both and cross-check them against each other.

## Scanned pages (no text layer)

Confirmed via empty `pdffonts` output in Step 1. Two options:

1. **A handful of pages** → rasterize with `pdftoppm` and read them
   visually, same as Step 3.
2. **Bulk extraction across many pages** → OCR:

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("target.pdf", dpi=300)
text = "\n".join(pytesseract.image_to_string(img) for img in images)
```

OCR quality depends heavily on scan quality — skewed or low-res scans
will produce errors. Spot-check the output against a rasterized page
before trusting it wholesale.

## Embedded images

```bash
pdfimages -png target.pdf /tmp/img      # extracts to /tmp/img-000.png, etc.
```

Two gotchas:

- **Vector graphics don't show up here.** Charts made in matplotlib,
  Excel, or R are drawn with page-content operators, not stored as
  image objects — `pdfimages` won't find them. Rasterize the whole
  page instead if a chart looks vector-drawn.
- **Tiny/blank extracted files are common.** These are usually masks
  or transparency layers, not real content. Filter by file size
  before assuming you've missed something.

## Embedded attachments

```bash
pdfdetach -saveall -o /tmp/attachments/ target.pdf
```

Common in business reports and PDF portfolios where a spreadsheet or
data file is bundled inside the PDF itself.

## Form fields

```python
from pypdf import PdfReader
reader = PdfReader("form.pdf")

text_fields = reader.get_form_text_fields()          # text inputs only
all_fields = reader.get_fields() or {}                # includes checkboxes, radios, dropdowns
for name, field in all_fields.items():
    print(name, "=", field.get("/V", ""), "type:", field.get("/FT", ""))
```

Use `get_fields()` rather than `get_form_text_fields()` whenever the
form has anything beyond plain text boxes — the latter silently
excludes checkboxes and dropdowns.

## Quick reference

| Need | Command / call |
|---|---|
| Page count, metadata | `pdfinfo target.pdf` |
| Does a text layer exist? | `pdffonts target.pdf` |
| Extract text, layout-aware | `pdftotext -layout target.pdf out.txt` |
| Extract text + tables | `pdfplumber` |
| View a page visually | `pdftoppm -jpeg -r 150 -f N -l N` |
| Extract raster images | `pdfimages -png target.pdf prefix` |
| Extract embedded files | `pdfdetach -saveall -o dir/` |
| Read form field values | `pypdf` → `reader.get_fields()` |
| OCR a scanned PDF | `pytesseract` + `pdf2image` |

## Out of scope

Filling in forms, creating new PDFs, merging/splitting, rotating,
watermarking, or encrypting — that's PDF *writing*, not reading. If
you also want a skill for that side, it's a natural companion skill
(`pdf-editing`) built around `pypdf`'s writer classes, `pdftk`, and
`qpdf`.
