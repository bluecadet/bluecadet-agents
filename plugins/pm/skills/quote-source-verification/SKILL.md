---
name: quote-source-verification
description: Use this skill whenever the user wants to verify, source, or trace a specific quote from a historical or public figure who has a digitized and/or scanned archival record. Trigger this any time the user asks to "find this quote," "verify this quote's source," "check if [person] really said this," or provides a specific quote and asks where it appears, what document it's from, or what date it was said — whether or not a PDF has been uploaded. Also trigger when the user has a batch/list of quotes still needing primary-source verification. This skill starts with a fast online-search pass against the figure's known institutional archive(s) before falling back to manual page-by-page work in a scanned/image-only archival PDF — do not jump straight to the PDF method without trying the fast path first. See references/known-figures.md for previously-confirmed source sets (currently: Harry S. Truman).
---

# Quote Source Verification

Locate and confirm a specific quote's exact date, source document, and context — starting with fast, searchable online sources, and falling back to manual page-by-page work in a scanned/image-only PDF only when the fast path comes up empty. Works for any figure who has both a searchable digital archive and a scanned bound-volume archive — not specific to one person. See `references/known-figures.md` for source sets already confirmed for specific figures.

---

## Step 0 — Fast path: search before touching any PDF

Always try this first, even when the user has uploaded a scanned PDF. Searching costs one or two tool calls; the manual PDF workflow costs five or more. Skipping straight to the PDF wastes effort the fast path would have saved.

1. **Identify the figure's primary-source sites.**
   - Check `references/known-figures.md` first — if this figure already has a confirmed source set, use it.
   - If not listed, identify the figure's own institutional archive(s): a presidential library, a national archive, a foundation, university special collections, etc. Ask the user if it isn't obvious.
   - Once a source set is confirmed working, add it to `references/known-figures.md` in the same format as the existing entries, so future verifications for this figure don't start from scratch.
2. Search the quote's exact text (or a distinctive fragment of it, in quotes) restricted to each identified source via a `site:` search.
3. **If any search returns a hit:**
   - Fetch the matching page directly from the primary institutional source itself — never from a third-party mirror, even if one shows up first or looks more convenient. Quotes like this tend to also appear on PBS, university course pages, history.state.gov, Goodreads, Substack posts, etc. Those are useful for *confirming* the quote is real, but the citation logged for the user's corpus must point to the primary institutional source, not the mirror.
   - Confirm the fetched text matches the quote exactly (word-for-word), and pull whatever the page states for date, document title, and context.
   - Log the result (see "Step 6 — Report the result" below) and **stop — do not proceed to the scanned-PDF workflow** for this quote.
4. **If no search returns a hit:** proceed to Step 1 below (the scanned-PDF method, starting with diagnosing the PDF). A clean miss across every identified source is itself informative — it suggests the quote may fall outside that source's known coverage (see "known gaps" for the figure in `references/known-figures.md`), be personal/unofficial material, or not be a genuine documented quote at all. This helps set expectations before committing to the slower method.

### Why the fast path has real limits — don't skip the scanned-PDF workflow entirely

Any single fast-path source has real coverage limits. A figure's official-role archive (e.g. a presidential library's "presidency" section) typically only covers that role, not material from before or after it. A broader institutional site may include much more, but often has scan-only, non-OCR'd collections that a web search can't reach at all. A miss on a fast-path source does not mean the material doesn't exist there, it means it isn't *searchable* there. Check `references/known-figures.md` for known gaps on a given figure's source set before assuming a miss is conclusive.

## When this applies vs. when it doesn't

**Use this skill when:**

- The user wants to verify, source, or trace a quote — a PDF may or may not already be involved.
- If a PDF is involved: it's a scanned bound volume (government publication, archive, old book), and `pdffonts` returns empty and/or `pdftotext` returns blank/garbage — confirms no usable text layer.
- The document has a chronological structure with a navigable index (List of Items, Table of Contents, etc.), for when the fast path misses and the scanned-PDF workflow is needed.
- You're looking for one specific quote, or verifying a short list of quotes one at a time.

**Don't use this for:**

- PDFs with a working text layer — just search the extracted text directly. (If a `pdf-reading`-type skill is available in your environment, defer to it for text-layer PDFs — this skill doesn't currently ship one.)
- Documents with no index/TOC and no way to narrow by date — bulk OCR may be more efficient than manual paging. (Same optional PDF-reading-skill note applies for OCR guidance.)
- Modern, small, or already-searchable documents.

## The scanned-PDF workflow (only after the Step 0 fast path misses)

### Step 1 — Diagnose the PDF once

```bash
pdfinfo document.pdf          # page count, size, creator/producer
pdffonts document.pdf         # empty output = no embedded fonts = image-only
pdftotext -f 1 -l 3 document.pdf -   # sample: blank/garbage confirms no text layer
```

If `pdffonts` is empty and `pdftotext` returns nothing meaningful, this skill's approach applies: extraction must happen visually, page by page, guided by the document's own index rather than keyword search.

### Step 2 — Find the front-matter index

Most archival volumes of this kind (official papers, congressional records, annual reports) include a chronological index near the front — item number, title, date, and printed page number for every entry.

```bash
pdftoppm -jpeg -r 100 -f 15 -l 15 document.pdf /tmp/toc
```

View the image. Step forward a few pages at a time through the front matter (typically pages ~5–35 of the raw PDF: cover, title page, preface, then the index itself) until you find it.

### Step 3 — Scan the index using the date as your compass

Page through the index visually, narrowing by whatever date information you have, even an approximate one ("sometime after V-E Day," "must be the year of his first inaugural"). Index entries are chronological, so this turns a 700-page search into a handful of page views.

```bash
pdftoppm -jpeg -r 100 -f 25 -l 25 document.pdf /tmp/toc25
pdftoppm -jpeg -r 100 -f 26 -l 26 document.pdf /tmp/toc26
# step forward/backward until the entry appears
```

Record: **item number, exact title, date, printed page number.**

If the date is genuinely unknown, it's usually faster to check secondary sources first (quote-verification sites, biography indexes, reputable quote-book compilations) to get a probable year, *then* come to the primary volume to confirm, rather than paging through an entire undated year blind.

### Step 4 — Convert printed page number → actual PDF page number

Scanned bound volumes have two numbering systems (roman-numeral front matter, arabic body pages) that don't match the raw PDF page count, because of covers and front matter. Calculate the offset **once per volume**:

```bash
pdftoppm -jpeg -r 100 -f 50 -l 50 document.pdf /tmp/sample
# View it — if the printed page shown is "10", offset = 50 - 10 = 40
```

Then: `PDF page = printed page + offset`, for every subsequent lookup in that same file.

### Step 5 — Rasterize the target page and confirm visually

```bash
pdftoppm -jpeg -r 100 -f <calculated_page> -l <calculated_page> document.pdf /tmp/pg
```

View the resulting image. Confirm:

- The page header's item number/date matches what the index promised.
- The quote text is present, word-for-word.
- Capture the surrounding paragraph(s) for context.

If off by a page or two (unnumbered plates, inserted pages), adjust ±1–3 and re-check the header — it always repeats the item number and date.

### Step 6 — Report the result

Always report back in this structure:

| Field | Value |
| --- | --- |
| Quote text | Transcribed exactly from the page image |
| Date | From the item header |
| Location | From context (e.g. "issued en route from Potsdam") or stated in the document |
| Source/Bibliography | `[Publication name], Item [#], p. [page]` |
| Verification status | **Verified** — confirmed directly against the primary document |
| Context | 1–2 sentences on what the document is and what surrounds the quote |

This is the strongest verification tier: direct confirmation against a primary source, not a secondary compilation or aggregator citation.

## Scaling to a batch of quotes

- **Always run the Step 0 fast-path search for every quote first**, even within a batch, it's cheap per-quote and needs no per-volume setup. Only group the *remaining* (fast-path-miss) quotes by probable year/volume before starting the scanned-PDF method — the index-location and offset-calculation costs (Steps 2 and 4) are paid once per volume, not once per quote.
- **A quote absent from the expected volume is itself informative** — it may belong to a different year, a different document type not covered by this source, or may not be a genuine quote from this person at all.
- **Avoid browsing broad page ranges "just to check."** Every rasterize + view has a real cost. Use the index's chronological ordering to jump directly rather than paging sequentially.
- If verifying many quotes across many candidate years, ask the user whether they want each candidate volume processed in full before moving to the next, or want to triage by likely-year first using secondary sources.
- Batch runs reuse fixed temp file paths (`/tmp/toc`, `/tmp/pg`, etc.) by default, so nothing persists across quotes. If a durable evidence trail matters for a given project, use per-quote-numbered paths instead (e.g. `/tmp/quote-03-pg142.jpg`).
