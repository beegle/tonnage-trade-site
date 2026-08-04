# Tonnage & Trade — the public site

The source of **tonnage-trade.com**. A static site built by one Python script and deployed to
GitHub Pages by `.github/workflows/pages.yml` on every push to `main` that touches `site/`.

```
site/     the generator, its content, and the built output
style/    the prose contract and the structured rule sets
```

This repository holds the site and the style rules and nothing else. Drafting, the data-platform
operations and the source specs live in separate repositories, which is why documents here may
refer to material you cannot see from this checkout.

## Build and preview

```bash
cd site && python3 build.py && python3 -m http.server 8000
```

Serve it rather than opening files directly: internal links are absolute. `site/README.md` carries
the full reference — content schema, section kinds, exhibit specs, access tiers.

## What is generated and what is edited

**Edit `site/content/`.** Everything else under `site/` except `assets/` and `build.py` is output:
`index.html`, the series directories, `topics/`, `data/`, `method/`, `subscribe/`, `404.html`,
`feed.xml`, `sitemap.xml`, `robots.txt`. Hand-editing generated files loses the edit on the next
build.

Add an article as a JSON file in `site/content/articles/`. The build fails rather than publishing a
record with a missing field, so a bad record cannot reach the site quietly.

## Rules that are correctness, not taste

`style/writing_rules.yml` and `style/chart_rules.yml` are canonical for every enumerable list —
banned openers, AI tells, measurable adjectives, terminology, prohibited chart types, integrity
tiers. `style/writing_style.md` is canonical for the reasoning and the rules a list cannot hold.

Three the generator enforces itself, because they are integrity controls rather than styling:

- **The value axis includes zero.** A cut axis misstates the size of a move.
- **A missing observation is a gap.** `null` breaks the trace; nothing is interpolated silently.
- **An estimate never looks observed.** It is drawn dashed, ends in an open circle, and is labelled.

A figure needs a named guarantor. `Showing` states the display universe as *K of N* plus the rule
that cut it. `Pre-specified` reads `Yes` only with a committed plan.

A note on em dashes, because the archive is inconsistent: the hand-authored site this replaced had
them stripped throughout, deliberately. The generator's records use them. Match the generator, so the
site reads as one voice, unless the owner decides otherwise.

## Before publishing

Set `release_id` in `site/content/site.json` to the data-lake release the figures were built
against. The folio names it, and the design language requires it to match the page. While it is
`null` the folio prints the date alone and the build says so.

Then look at every changed page in a browser, at desktop and mobile width, before pushing. The
structure checking out is not the same as having seen it: a chart can be geometrically valid and
still unreadable, and a headline can contradict the exhibit beneath it.
