---
name: prototype-change-manifest
description: Write the CHANGES.md handoff document that goes with a designer's AI-built code prototype, so a developer (or their coding agent) can implement the design in the production codebase without reverse-engineering the prototype. Use this whenever a prototype is ready to hand to developers — HTML, React, Svelte, Astro, Twig, a Netlify or Vercel preview, Claude Design or Figma Make output — and whenever someone says "hand this off", "write up the changes", "what changed vs. the live site", "spec this for engineering", "document this for the devs", or "make a changelog", even if they don't say "manifest". Also use it mid-project when a designer wants to log what they've decided so far.
---

# Prototype Change Manifest

## Why this exists

A prototype is a finished picture. Developers don't need the picture, they need to know what it's *for*: which parts are new, which existing parts changed, why, and how things are meant to behave. That layer of intent is what a designer's agent had in its head while building and what evaporates the moment the prototype is handed over. Without it, the developer reverse-engineers decisions from generated markup. With it, they translate.

The manifest is written entirely in **design language**. It does not need to know the production codebase's component names, template structure, or stack. Mapping the manifest onto the real implementation is the developer's job; they have the repo and the context to do it cheaply. The designer's job is to make the intent so clear that the mapping is obvious.

## The one test

Every entry in the manifest has to pass this: **could a developer implement it correctly without ever opening the prototype, and without guessing what the designer meant?**

The prototype stays available as the visual reference and the acceptance check. But if the manifest only makes sense alongside the prototype, it isn't done.

## Inputs

1. **The prototype** — source files and/or a preview URL. Read the actual markup, styles, and scripts. Don't work from a screenshot alone; the prototype's behavior and states live in the code.
2. **The current state** — the live page URL, staging URL, screenshots, or a note that this is a net-new page. Without a current state you can't say what changed, only what exists. If it's new, say so and the "modified" and "removed" sections will be "None".
3. **The designer's intent**, wherever it lives — the conversation with their agent, a brief, notes, a Figma link, a Slack thread. Ask for it. The manifest's *Why* lines come from here, not from your inference. When you have to infer, mark it `(inferred)` so the developer knows to check.
4. **A decisions log**, if the designer kept one (see "Mid-project use" below).

Ask once for anything missing. Don't guess at intent.

## Output

A single file, `CHANGES.md`, next to the prototype or wherever the user asks. Use `assets/CHANGES.template.md` exactly — same sections, same order, same headings — so developers learn to scan it once and can rely on it every time.

Text only. Link to the prototype, screenshots, and assets; don't embed them.

## How to write a good entry

Describe things the way you'd explain them to a competent developer who has never seen this project. Name page regions and elements by what they *are* ("the hero", "the three-column feature row", "the sticky sub-navigation"), not by what the prototype's code calls them (`<div class="section-2">`) and not by what you guess the production code calls them.

Each entry has:

- **What it is** — the element, its parts, and its content slots. For a card: "image, eyebrow label, title, two-line description, the whole card is a link." Be literal about structure, because structure is what maps to components.
- **What changed** — for modified things, the specific delta vs. the current page: added, removed, moved, resized, restyled, rebehaved. "Adds a secondary CTA under the primary button" beats "updated the hero."
- **Why** — one line of design intent, in the designer's words when possible. This is the most valuable line in the entry: when the literal spec doesn't fit the codebase, the developer uses *Why* to find the right compromise. Mark `(inferred)` if it's your guess.
- **Deliberate or default** — was this a considered choice or something the agent generated that the designer didn't push back on? Developers treat these very differently. A deliberate 12px gap gets matched; a default 12px gap gets replaced with the system's spacing scale. If the designer can't say, write `unknown`.
- **Behavior and states** — hover, focus, active, empty, loading, error, "no image", "very long title", "many items", "one item". Only what the prototype actually defines. If an important state is undefined, that's an *Open question*, not something to invent.
- **Responsive** — only where behavior differs by viewport. Describe the change ("stacks vertically, image moves above text"), not the breakpoint value from the prototype's CSS.

Design values (colors, spacing, type sizes) go in as **what they mean**, not what the prototype's CSS says: "brand primary", "the largest heading size on the site", "a full spacing step tighter than the current section gap". If the designer worked with real tokens or a Figma style name, use that name. Raw hex or pixel values are fine as a *secondary* note in parentheses, because they help the developer find the nearest token; they are never the spec.

Things to refuse to write:

- "Matches the prototype" or "see prototype" as a description.
- Prototype CSS or markup pasted in as the spec.
- Guesses about how the production codebase is built ("should be a new block", "probably reuses the card component"). You don't know, and a wrong guess costs more than no guess. If it seems relevant, put it in *Open questions* as a question.
- Anything vague enough that two developers would build it differently.

## Process

1. Read the prototype source top to bottom. Inventory every distinct region and every interactive element before classifying anything.
2. Read the current state the same way.
3. Read the intent source and the decisions log if there is one. Note which prototype elements have a stated reason and which don't; the ones that don't get `(inferred)` or `default`.
4. For each region: **new**, **modified**, **unchanged**, or **removed**. Be honest and complete about *unchanged*; that section is what lets a developer trust the rest.
5. Write the manifest from the template. Every section is present; empty ones say "None".
6. Reread as a developer. Pick three entries at random and ask whether you could build them from the text alone and whether you'd know what to do if the codebase doesn't have an exact match. Fix any that fail.
7. Report back with the file path, counts (new / modified / open questions), and list the open questions inline so the designer can answer them before the handoff goes out.

## Mid-project use

If the designer asks to log decisions while they're still working, keep a `DECISIONS.md` next to the prototype: dated, short entries of "what / why / deliberate or default". Delete entries for things that were thrown away. It's for the designer and for producing the final manifest; it does not go to developers. When the handoff manifest is generated, read it first — it's the best source of *Why* lines.

Don't push a decisions log during early throwaway exploration. It earns its keep once a direction is chosen.

## Example entry

```markdown
### Hero — modified
**What it is:** Full-width band at the top of the page. Left column: eyebrow, headline, one-paragraph intro, primary button, and a new secondary text link under it. Right column: a single landscape image.
**What changed:** Image moves from left to right. Adds the secondary link. Headline drops to the second-largest heading size.
**Why:** Client wants a "watch the film" path without competing with the main CTA; the smaller headline gives the image more weight.
**Deliberate or default:** Deliberate.
**States:** No secondary link supplied → identical to the current hero layout.
**Responsive:** On narrow viewports the image moves above the text and the two CTAs stack.
```

Versus what not to write:

```markdown
### Hero
Updated hero to match the new design, see prototype. Should probably be a variant of the existing hero block.
```
