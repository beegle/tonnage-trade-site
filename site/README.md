# site/ — the public website

A static site built by one Python script, deployed to GitHub Pages. No framework, no CDN, no
client JavaScript, no external fonts. Every exhibit is hand-computed inline SVG, so a figure can be
re-derived when a number changes.

Form is governed by the **Tonnage & Trade Design Language, version 1** — Warm Paper, serif for
prose and sans for data, three weights of line and no boxes. Prose is governed by
`../style/writing_style.md` and the **`publishing-checks`** skill.

## Build and preview

```bash
cd site && python3 build.py && python3 -m http.server 8000
```

Then open `http://localhost:8000`. Serve it — do not open the files directly, because internal
links are absolute.

| Flag | Use |
|---|---|
| `--base /repo` | build for a project page at `https://<user>.github.io/<repo>/` |
| `--clean` | delete generated files before rebuilding |

## Layout

```
content/site.json            settings: name, nav, kinds, access tiers, release id
content/articles/*.json      one file per article
assets/css/tokens.css        Warm Paper tokens — the only place colour and type are defined
assets/css/site.css          components; every value transcribed from the design language
build.py                     the generator, including the SVG exhibit and sparkline routines
```

Everything else in this directory is generated: `index.html`, the four series directories,
`topics/`, `data/`, `method/`, `subscribe/`, `404.html`, `feed.xml`, `sitemap.xml`, `robots.txt`.
Do not hand-edit them — edit the content JSON and rebuild.

## Deploying

```bash
./publish.sh "commit subject"      # build, sync, commit, push
./publish.sh --dry-run             # build and sync, show the diff, push nothing
```

`publish.sh` is the only supported route to production. It builds, copies a
whitelist into a clone of `beegle/tonnage-trade-site` (kept at `~/code/tonnage-trade-site`,
override with `TNT_SITE_CLONE`), and pushes `main`. GitHub Actions builds and
deploys on every push touching `site/`, so publishing is that one command.

The script exists rather than a plain `git push` because this working repo also
holds `data/` and `articles/` — production runbooks, the droplet address, an
open privilege finding, and unsubmitted drafts. None of it may reach a public
repository, which is why the public history was started fresh and why the
script refuses to push if `data/`, `articles/`, or any operational string
appears in the staged tree. It also refuses if `site/CNAME` is missing, which
would silently drop the custom domain.

Pages is configured as **Source: GitHub Actions**. If it is ever switched back
to branch-serving, the site 404s: the repo has no `index.html` at its root.

## Adding an article

Add a JSON file to `content/articles/` and rebuild. Required fields: `slug`, `kind`, `title`,
`standfirst`, `byline`, `min_tier`, `as_of`, `published_at`, `ledger_finding`, `ledger_evidence`,
`sections`. `kind` is one of `river_note`, `special_report`, `analysis`, `note`, and it decides the
URL prefix. The build fails rather than publishing a record with a missing field.

`ledger_finding` is the sentence the front-page ledger shows. It states a finding a reader can
agree or disagree with — not a topic label.

### Section kinds

`prose` · `key_figure` · `exhibit` · `supertable` · `pull_quote` · `watch_list` · `docbox` ·
`divider`. Each takes `width` of `reading` (default), `wide` or `full`.

### Exhibits

An exhibit spec carries `id`, `type`, `size` (`full` 900×300 or `lead` 420×250), `labels`,
`series`, `value_label`, `aria_label`, `caption` and a ten-slot `docbox`.

Three rules the generator enforces, because they are integrity controls rather than styling:

- **The value axis always includes zero.** A cut value axis misstates the size of a move. Where
  that compresses the trace, the printed start and end values carry the precision. Set `value_max`
  when a measure has a natural ceiling, as a percentage does.
- **A missing observation is a gap.** Write `null` in the series and the trace breaks across it.
  Nothing is interpolated silently.
- **An estimate never looks observed.** Set `estimated_from` to the index where estimation begins;
  that segment is drawn dashed, its endpoint is an open circle, and it is labelled `estimate`.

A figure needs a named guarantor in `Built by`. `Showing` states the display universe as
*K of N* plus the rule that cut it. `Pre-specified` reads `Yes` only with a committed plan.

## Access tiers

`min_tier` is `free`, `entry`, `pro` or `enterprise`. This site has no accounts, so anything above
`free` publishes as its opening section followed by the subscriber boundary, which lists how many
sections remain and what each one tests. Withheld content is not sent to the browser — there is no
fade, no blur, and nothing hidden with CSS.

## Before publishing

Set `release_id` in `content/site.json` from `get_release_status`. The folio names the data-lake
release each page was built against, and the design language requires it to match the figures on
the page. While it is `null` the folio prints the date alone and the build says so.
