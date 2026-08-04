#!/usr/bin/env python3
"""Build the Tonnage & Trade static site.

Reads `content/site.json` and `content/articles/*.json`, writes plain HTML into
this directory. No dependencies beyond the standard library, no CDN, no client
JavaScript: every exhibit is hand-computed inline SVG so a figure can be
re-derived when a number changes.

    python3 build.py                 # build for a root domain
    python3 build.py --base /tonnage # build for a GitHub project page
    python3 build.py --clean         # remove generated files first

Layout and every absolute value come from the Tonnage & Trade Design Language,
version 1. Section numbers in the comments below refer to it.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"

# Files and directories build.py owns. --clean removes exactly these.
GENERATED_DIRS = ["river-notes", "reports", "analysis", "notes", "topics",
                  "data", "method", "subscribe"]
GENERATED_FILES = ["index.html", "404.html", "feed.xml", "sitemap.xml", "robots.txt"]

# ---------------------------------------------------------------------------
# Warm Paper — the six values, transcribed from design language §01.
# ---------------------------------------------------------------------------

INK = "#1b1b1a"
QUIET = "#6f6c66"
BAND = "#e7e6e0"
SIGNAL = "#b0221b"
COUNTER = "#2c6fbb"
GRID = "rgba(0,0,0,.08)"
AXIS = "rgba(0,0,0,.15)"

SANS = "Inter,'Helvetica Neue',system-ui,sans-serif"

# Exhibit sizes (§06). Margin note is drawn by the sparkline routines.
EXHIBIT_SIZES = {"full": (900, 300), "lead": (420, 250)}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value or "")).strip()


def first_sentence(value: str) -> str:
    text = strip_tags(value)
    match = re.search(r"^(.+?[.!?])(\s|$)", text)
    return match.group(1) if match else text


# ---------------------------------------------------------------------------
# Dates. Everything a reader sees is a plain calendar date; the Atom feed keeps
# the RFC 3339 form it requires.
# ---------------------------------------------------------------------------

def parse_date(value) -> date | None:
    if not value:
        return None
    return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


def long_date(value) -> str:
    day = parse_date(value)
    return f"{day:%B} {day.day}, {day.year}" if day else ""


def full_date(value) -> str:
    day = parse_date(value)
    return f"{day:%A}, {day:%B} {day.day}, {day.year}" if day else ""


def short_date(value) -> str:
    day = parse_date(value)
    return f"{day:%b} {day.day}" if day else ""


def rfc3339(value) -> str:
    day = parse_date(value)
    return f"{day.isoformat()}T12:00:00Z" if day else ""


# ---------------------------------------------------------------------------
# Scales
# ---------------------------------------------------------------------------

def nice_ceiling(value: float) -> float:
    """Round a value up to a readable axis maximum."""
    if value <= 0:
        return 1.0
    import math

    magnitude = 10 ** math.floor(math.log10(value))
    for step in (1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 7.5, 10):
        candidate = step * magnitude
        if candidate >= value:
            return candidate
    return 10 * magnitude


def fmt(value: float, pattern: str) -> str:
    return pattern % value


# ---------------------------------------------------------------------------
# Exhibits (§06)
#
# Transparent background, no frame, no legend where a direct label will do.
# Subject series 2.1px signal red. Horizontal gridlines only, four at most.
# The value axis always includes zero — a cut value axis is a lie about the
# size of a move — and the printed start and end values carry the precision
# the trace compresses.
# ---------------------------------------------------------------------------

def render_line_exhibit(spec: dict) -> str:
    width, height = EXHIBIT_SIZES[spec.get("size", "full")]
    pad_top, pad_right, pad_bottom, pad_left = 36, 104, 30, 8

    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    series = spec["series"]
    value_fmt = spec.get("value_format", "%.2f")
    values = [v for s in series for v in s["data"] if v is not None]
    top = float(spec.get("value_max") or nice_ceiling(max(values)))

    def x_of(i: int, n: int) -> float:
        return pad_left if n < 2 else pad_left + plot_w * i / (n - 1)

    def y_of(v: float) -> float:
        return pad_top + plot_h * (1 - v / top)

    parts: list[str] = []

    # The value axis is labelled once, top-left, with its units and its full
    # extent (§06). Naming the extent there rather than beside each gridline
    # keeps the scale recoverable without putting text where a trace runs.
    parts.append(
        f'<text x="{pad_left}" y="16" font-family="{SANS}" font-size="10.5" '
        f'fill="{QUIET}">{esc(spec["value_label"])} · axis 0 to '
        f"{esc(fmt(top, value_fmt))}</text>"
    )

    # Four gridlines at most, horizontal only. Zero is the baseline axis.
    for step in range(4):
        y = y_of(top * step / 3)
        stroke = AXIS if step == 0 else GRID
        parts.append(
            f'<line x1="{pad_left}" y1="{y:.1f}" x2="{pad_left + plot_w}" '
            f'y2="{y:.1f}" stroke="{stroke}" stroke-width="1"/>'
        )

    for index, s in enumerate(series):
        data = s["data"]
        n = len(data)
        role = s.get("role", "subject" if index == 0 else "comparison")
        colour = INK if role == "subject" else QUIET
        stroke_w = 2.1 if role == "subject" else 1.25
        est_from = s.get("estimated_from")

        # A missing observation is a gap, never an interpolation: the trace
        # breaks across it and the caption says so.
        points = [None if v is None else (x_of(i, n), y_of(v)) for i, v in enumerate(data)]

        def path(pairs) -> str:
            return " ".join(f"{x:.1f},{y:.1f}" for x, y in pairs)

        def runs(sliced: list) -> list[list]:
            out: list[list] = []
            for p in sliced:
                if p is None:
                    out.append([])
                elif out:
                    out[-1].append(p)
                else:
                    out.append([p])
            return [r for r in out if len(r) > 1]

        solid_end = est_from if est_from is not None else n - 1
        for run in runs(points[: solid_end + 1]):
            parts.append(
                f'<polyline fill="none" stroke="{colour}" stroke-width="{stroke_w}" '
                f'stroke-linejoin="round" stroke-linecap="round" points="{path(run)}"/>'
            )
        # An estimated segment is drawn dashed so the page never implies
        # observation for an estimated value.
        if est_from is not None and est_from < n - 1:
            for run in runs(points[est_from:]):
                parts.append(
                    f'<polyline fill="none" stroke="{colour}" stroke-width="{stroke_w}" '
                    f'stroke-linejoin="round" stroke-dasharray="4 3" points="{path(run)}"/>'
                )

        if role != "subject":
            continue

        # Where an estimated tail follows, the last observed point is marked
        # and printed, so the reader can see exactly where observation stops.
        if est_from is not None and est_from < n - 1 and data[est_from] is not None:
            ox, oy = points[est_from]
            parts.append(
                f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="2.4" fill="{INK}"/>'
                f'<text x="{ox:.1f}" y="{oy + 17:.1f}" text-anchor="middle" '
                f'font-family="{SANS}" font-size="11" fill="{QUIET}" '
                f'>{esc(fmt(data[est_from], value_fmt))}</text>'
            )

        observed = [(i, p) for i, p in enumerate(points) if p is not None]
        first_i, (first_x, first_y) = observed[0]
        last_i, (last_x, last_y) = observed[-1]
        estimated_endpoint = est_from is not None and last_i >= est_from

        # Start value, printed quiet below the trace so it cannot sit on it.
        parts.append(
            f'<circle cx="{first_x:.1f}" cy="{first_y:.1f}" r="2.4" fill="{QUIET}"/>'
            f'<text x="{first_x + 2:.1f}" y="{first_y + 17:.1f}" font-family="{SANS}" '
            f'font-size="11" fill="{QUIET}">{esc(fmt(data[first_i], value_fmt))}</text>'
        )

        # Endpoint: a 4px circle in signal red and the printed value beside it.
        # An estimate gets the open circle filled with paper instead (§06).
        if estimated_endpoint:
            parts.append(
                f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="4.2" fill="#fcfbf9" '
                f'stroke="{SIGNAL}" stroke-width="1.4"/>'
            )
        else:
            parts.append(
                f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="4" fill="{SIGNAL}"/>'
            )
        parts.append(
            f'<text x="{last_x + 10:.1f}" y="{last_y + 5:.1f}" font-family="{SANS}" '
            f'font-size="14" font-weight="600" fill="{SIGNAL}" '
            f'>{esc(fmt(data[last_i], value_fmt))}</text>'
        )
        if estimated_endpoint:
            parts.append(
                f'<text x="{last_x + 10:.1f}" y="{last_y + 20:.1f}" font-family="{SANS}" '
                f'font-size="10.5" fill="{QUIET}">estimate</text>'
            )
        if len(series) > 1:
            parts.append(
                f'<text x="{last_x + 10:.1f}" y="{last_y - 10:.1f}" font-family="{SANS}" '
                f'font-size="10.5" fill="{QUIET}">{esc(s["label"])}</text>'
            )

    # Time labels, 10.5px quiet sans, under the points they belong to.
    labels = spec.get("point_labels") or spec.get("labels") or []
    n = len(series[0]["data"])
    for i, label in enumerate(labels[:n]):
        if not label:
            continue
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        x = x_of(i, n)
        parts.append(
            f'<text x="{x:.1f}" y="{height - 10}" text-anchor="{anchor}" '
            f'font-family="{SANS}" font-size="10.5" fill="{QUIET}">{esc(label)}</text>'
        )

    body = "".join(parts)
    return (
        f'<svg id="{esc(spec["id"])}" viewBox="0 0 {width} {height}" width="{width}" '
        f'height="{height}" role="img" aria-label="{esc(spec["aria_label"])}" '
        f'preserveAspectRatio="xMidYMid meet">{body}</svg>'
    )


# ---------------------------------------------------------------------------
# Datawords and margin notes (§07)
#
# Drawn inside a 4px inset on every side so the endpoint circle can never clip.
# The band is the range of the earlier readings — a field, not a frame.
# ---------------------------------------------------------------------------

def _spark_geometry(data: list[float], width: float, height: float, inset: float):
    lo, hi = min(data), max(data)
    # Headroom above and below the observed range, so the normal-range band
    # reads as a field inside the box rather than filling it edge to edge.
    pad = ((hi - lo) or 1.0) * 0.12
    lo, hi = lo - pad, hi + pad
    span = hi - lo
    usable_w = width - 2 * inset
    usable_h = height - 2 * inset

    def x_of(i: int) -> float:
        return inset + (usable_w * i / (len(data) - 1) if len(data) > 1 else 0)

    def y_of(v: float) -> float:
        return inset + usable_h * (1 - (v - lo) / span)

    return x_of, y_of


def render_dataword(data: list[float], label: str) -> str:
    """Inline sparkline, 72 x 22, for use in a line of prose."""
    x_of, y_of = _spark_geometry(data, 72, 22, 4)
    prior = data[:-1] or data
    band_top, band_bottom = y_of(max(prior)), y_of(min(prior))
    points = " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(data))
    return (
        f'<span class="dataword"><svg viewBox="0 0 72 22" width="72" height="22" '
        f'role="img" aria-label="{esc(label)}">'
        f'<rect x="4" y="{band_top:.1f}" width="64" height="{band_bottom - band_top:.1f}" fill="{BAND}"/>'
        f'<polyline fill="none" stroke="{INK}" stroke-width="1" stroke-linejoin="round" points="{points}"/>'
        f'<circle cx="{x_of(len(data) - 1):.1f}" cy="{y_of(data[-1]):.1f}" r="2" fill="{SIGNAL}"/>'
        f"</svg></span>"
    )


def render_margin_spark(data: list[float], label: str) -> str:
    """Margin-note sparkline, 200 x 52 — preferred where the graphic needs
    its own anchors."""
    x_of, y_of = _spark_geometry(data, 200, 52, 4)
    prior = data[:-1] or data
    band_top, band_bottom = y_of(max(prior)), y_of(min(prior))
    points = " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(data))
    return (
        f'<svg viewBox="0 0 200 52" width="200" height="52" role="img" '
        f'aria-label="{esc(label)}">'
        f'<rect x="0" y="{band_top:.1f}" width="200" height="{band_bottom - band_top:.1f}" fill="{BAND}"/>'
        f'<polyline fill="none" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round" points="{points}"/>'
        f'<circle cx="{x_of(len(data) - 1):.1f}" cy="{y_of(data[-1]):.1f}" r="2.6" fill="{SIGNAL}"/>'
        f"</svg>"
    )


# ---------------------------------------------------------------------------
# The documentation box (§06) — ten slots, above a 1px rule, 11.5px quiet.
# A slot is omitted only when it cannot apply, never because it is
# inconvenient. A figure without a named guarantor does not publish.
# ---------------------------------------------------------------------------

DOC_SLOTS = ["Source", "Grain", "Showing", "Period", "n", "Units",
             "Evidence class", "Uncertainty", "Built by", "Pre-specified"]


def render_docbox(fields: dict, tight: bool = False) -> str:
    if not fields:
        return ""
    ordered = [(k, fields[k]) for k in DOC_SLOTS if fields.get(k)]
    ordered += [(k, v) for k, v in fields.items() if k not in DOC_SLOTS and v]
    rows = "".join(f"<div><strong>{esc(k)}:</strong> {esc(v)}</div>" for k, v in ordered)
    cls = "docbox docbox--tight" if tight else "docbox"
    return f'<div class="{cls}">{rows}</div>'


def exhibit_data_attrs(doc: dict) -> str:
    """The provenance attributes every chart panel carries."""
    pairs = {
        "data-source": doc.get("Source", ""),
        "data-as-of": doc.get("Period", ""),
        "data-period": doc.get("Period", ""),
        "data-units": doc.get("Units", ""),
        "data-evidence-class": doc.get("Evidence class", ""),
    }
    return " ".join(f'{k}="{esc(v)}"' for k, v in pairs.items() if v)


def render_exhibit(spec: dict) -> str:
    doc = spec.get("docbox", {})
    svg = render_line_exhibit(spec)
    caption = spec.get("caption", "")
    return (
        f'<figure class="exhibit" {exhibit_data_attrs(doc)}>{svg}'
        f"<figcaption>{caption}</figcaption>{render_docbox(doc)}</figure>"
    )


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def render_section(section: dict) -> str:
    kind = section["kind"]
    width = section.get("width", "reading")
    cls = f" section--{width}" if width != "reading" else ""

    if kind == "prose":
        return f'<div class="prose{cls}">{section["html"]}</div>'

    if kind == "key_figure":
        change_cls = {"negative": " is-signal", "positive": " is-counter"}.get(
            section.get("change_dir", ""), ""
        )
        spark = ""
        if section.get("spark"):
            caption = section.get("spark_caption", "")
            spark = (
                f'<div class="marginnote">{render_margin_spark(section["spark"], section.get("spark_label", ""))}'
                f'<div class="marginnote__caption">{caption} '
                f"Grey band spans the range of the earlier readings.</div></div>"
            )
        source = ""
        if section.get("source_line"):
            source = render_docbox(
                {"Source": section["source_line"],
                 "Units": section.get("unit", ""),
                 "Evidence class": section.get("evidence_class", "")},
                tight=True,
            )
        return (
            f'<div class="keyfig{cls}">'
            f'<div class="keyfig__label">{esc(section["label"])}</div>'
            f'<div class="keyfig__row">'
            f'<span class="keyfig__value">{esc(section["value"])}</span>'
            f'<span class="keyfig__unit">{esc(section.get("unit", ""))}</span>'
            f'<span class="keyfig__change{change_cls}">{esc(section.get("change", ""))}</span>'
            f"</div>"
            f'<p class="keyfig__context">{esc(section.get("context", ""))}</p>'
            f"{spark}{source}</div>"
        )

    if kind == "exhibit":
        return f'<div class="{cls.strip() or "section"}">{render_exhibit(section["exhibit"])}</div>'

    if kind == "supertable":
        cols = section["columns"]
        head = "".join(
            f'<th scope="col"{" class=\"n\"" if c.get("numeric") else ""}>{esc(c["label"])}</th>'
            for c in cols
        )
        body = ""
        for row in section["rows"]:
            cells = "".join(
                f'<td{" class=\"n\"" if cols[i].get("numeric") else ""}>{esc(cell)}</td>'
                for i, cell in enumerate(row)
            )
            body += f"<tr>{cells}</tr>"
        return (
            f'<figure class="supertable{cls}"><table>'
            f'<caption>{section.get("caption", "")}</caption>'
            f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
            f'{render_docbox(section.get("docbox", {}))}</figure>'
        )

    if kind == "pull_quote":
        cite = f"<footer>{esc(section['cite'])}</footer>" if section.get("cite") else ""
        return f'<blockquote class="pullquote{cls}"><p>{esc(section["text"])}</p>{cite}</blockquote>'

    if kind == "watch_list":
        rows = "".join(
            f'<tr><td class="when">{esc(i["when"])}</td>'
            f'<td class="claim">{esc(i["claim"])}</td>'
            f'<td class="basis">{esc(i["basis"])}</td></tr>'
            for i in section["items"]
        )
        return (
            f'<div class="watchlist{cls}">'
            f'<h2 class="watchlist__title">{esc(section["title"])}</h2>'
            f'<table><thead><tr><th scope="col">By when</th>'
            f'<th scope="col">The call</th><th scope="col">On what basis</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>"
        )

    if kind == "docbox":
        fields = dict(section.get("fields", {}))
        if section.get("as_of"):
            fields.setdefault("As of", long_date(section["as_of"]))
        return render_docbox(fields)

    if kind == "divider":
        return '<hr class="divider">'

    raise ValueError(f"unknown section kind: {kind}")


def describe_section(section: dict) -> str | None:
    """One line naming what a withheld section tests, for the boundary (§09)."""
    kind = section["kind"]
    if kind == "docbox":
        return None
    if kind == "key_figure":
        return f'The figure — {section["label"]}, with its context and history'
    if kind == "exhibit":
        return f'An exhibit — {first_sentence(section["exhibit"].get("caption", ""))}'
    if kind == "supertable":
        return f'A table — {first_sentence(section.get("caption", ""))}'
    if kind == "pull_quote":
        return "The reading rule the analysis turns on"
    if kind == "watch_list":
        return f'{section["title"]} — dated calls that can be checked against the print'
    if kind == "prose":
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", section.get("html", ""))
        return strip_tags(heading.group(1)) if heading else "The argument, continued"
    return None


# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------

class Site:
    def __init__(self, settings: dict, articles: list[dict], base: str):
        self.s = settings
        self.articles = articles
        self.base = base.rstrip("/")

    def url(self, path: str) -> str:
        return f"{self.base}{path}" if path.startswith("/") else path

    def article_url(self, article: dict) -> str:
        path = self.s["kinds"][article["kind"]]["path"]
        return self.url(f"/{path}/{article['slug']}.html")

    def is_public(self, article: dict) -> bool:
        tiers = self.s["tiers"]
        return tiers[article["min_tier"]]["level"] <= tiers[self.s["public_tier"]]["level"]

    def access_label(self, article: dict) -> str:
        return self.s["tiers"][article["min_tier"]]["label"]

    # -- masthead (§04) -----------------------------------------------------

    def masthead(self, current: str | None, front: bool, folio_date: str | None) -> str:
        nav = "".join(
            f'<a href="{self.url(item["href"])}"'
            f'{" class=\"is-signal\"" if item.get("signal") else ""}'
            f'{" aria-current=\"page\"" if item["href"] == current else ""}'
            f">{esc(item['label'])}</a>"
            for item in self.s["nav"]
        )
        name = esc(self.s["name"])
        home = self.url("/")
        if not front:
            return (
                f'<header class="masthead masthead--interior"><div class="masthead__top">'
                f'<a class="masthead__name" href="{home}">{name}</a>'
                f"<nav aria-label=\"Sections\">{nav}</nav></div></header>"
            )

        release = self.s.get("release_id")
        right = full_date(folio_date)
        if release:
            right += f" · release {release}"
        return (
            f'<header class="masthead"><div class="masthead__top">'
            f'<a class="masthead__name" href="{home}">{name}</a>'
            f'<nav aria-label="Sections">{nav}</nav></div>'
            f'<div class="masthead__rule"></div>'
            f'<div class="folio"><span>{esc(self.s["scope"])}</span>'
            f"<span>{esc(right)}</span></div></header>"
        )

    def footer(self) -> str:
        links = "".join(
            f'<a href="{self.url(i["href"])}">{esc(i["label"])}</a>'
            for i in self.s["footer_nav"]
        )
        year = max((parse_date(a["published_at"]).year for a in self.articles), default=2026)
        return (
            f'<footer class="foot"><nav aria-label="More">{links}</nav>'
            f'<span>{esc(self.s["name"])} · {year}</span></footer>'
        )

    # -- page shell ---------------------------------------------------------

    def page(self, *, title: str, description: str, body: str, current: str | None = None,
             front: bool = False, folio_date: str | None = None, canonical: str = "") -> str:
        full_title = title if title == self.s["name"] else f'{title} — {self.s["name"]}'
        canon = ""
        if canonical and self.s.get("base_url"):
            canon = f'<link rel="canonical" href="{esc(self.s["base_url"].rstrip("/") + canonical)}">'
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
{canon}
<link rel="icon" type="image/svg+xml" href="{self.url('/assets/favicon.svg')}">
<link rel="alternate" type="application/atom+xml" title="{esc(self.s['name'])}" href="{self.url('/feed.xml')}">
<link rel="stylesheet" href="{self.url('/assets/css/tokens.css')}">
<link rel="stylesheet" href="{self.url('/assets/css/site.css')}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="desk"><div class="page">
{self.masthead(current, front, folio_date)}
<main id="main">
{body}
</main>
{self.footer()}
</div></div>
</body>
</html>
"""

    # -- the front page (§05) ----------------------------------------------

    def front_page(self) -> str:
        lead_article = next((a for a in self.articles if a.get("featured")), self.articles[0])
        lead = lead_article["lead"]

        paragraphs = "".join(f"<p>{p}</p>" for p in lead["paragraphs"])
        kind = self.s["kinds"][lead_article["kind"]]
        access = self.access_label(lead_article)
        eyebrow = f'{kind["label"]} · {self.s["scope"]} · {access} to read'

        byline = (
            f'{esc(lead_article["byline"])} · published {long_date(lead_article["published_at"])} · '
            f'figures as of {long_date(lead_article["as_of"])}'
        )

        lead_block = (
            f'<div class="lead"><div class="lead__body">'
            f'<div class="eyebrow">{esc(eyebrow)}</div>'
            f'<h1 class="headline"><a href="{self.article_url(lead_article)}" '
            f'style="color:inherit;border-bottom-color:rgba(0,0,0,.15)">{esc(lead_article["title"])}</a></h1>'
            f'<p class="standfirst">{esc(lead_article["standfirst"])}</p>'
            f'{paragraphs}<div class="byline">{byline}</div></div>'
            f'<div class="lead__aside">{render_exhibit(lead["exhibit"])}</div></div>'
        )

        # The ledger — everything published, newest first, nothing ranked.
        rows = ""
        for a in self.articles:
            kind = self.s["kinds"][a["kind"]]
            series_signal = " class=\"is-signal\"" if a["kind"] in ("special_report", "analysis") else ""
            rows += (
                f"<tr><td>{esc(short_date(a['published_at']))}</td>"
                f"<td{series_signal}>{esc(kind['label'])}</td>"
                f'<td class="ledger__finding"><a href="{self.article_url(a)}">{esc(a["ledger_finding"])}</a></td>'
                f"<td>{esc(a['ledger_evidence'])}</td></tr>"
            )

        count = len(self.articles)
        ledger = (
            f'<section class="stack--tight" style="display:flex;flex-direction:column;gap:10px">'
            f'<div class="eyebrow eyebrow--quiet">The ledger — everything published, newest first, nothing ranked</div>'
            f'<div class="ledger-wrap"><table class="ledger">'
            f'<colgroup><col class="c-date"><col class="c-series"><col><col class="c-evid"></colgroup>'
            f'<thead><tr><th scope="col">Date</th><th scope="col">Series</th>'
            f'<th scope="col">Finding</th><th scope="col">Evidence</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>'
            f'<div class="ledger__count">Showing {count} of {count} published '
            f'{"item" if count == 1 else "items"}, ordered by publication date.</div></section>'
        )

        return self.page(
            title=self.s["name"],
            description=self.s["description"],
            body=lead_block + ledger,
            front=True,
            folio_date=lead_article["published_at"],
            canonical="/",
        )

    # -- an article ---------------------------------------------------------

    def article_page(self, article: dict) -> str:
        kind = self.s["kinds"][article["kind"]]
        public = self.is_public(article)
        access = self.access_label(article)
        eyebrow = f'{kind["label"]} · {self.s["scope"]} · {access} to read'

        tags = ""
        if article.get("tags"):
            links = ", ".join(
                f'<a href="{self.url("/topics/" + slugify(t) + ".html")}">{esc(t)}</a>'
                for t in article["tags"]
            )
            tags = f'<div class="tags">Topics: {links}</div>'

        byline = (
            f'{esc(article["byline"])} · published {long_date(article["published_at"])} · '
            f'figures as of {long_date(article["as_of"])}'
        )

        head = (
            f'<div class="article__masthead"><div class="eyebrow">{esc(eyebrow)}</div>'
            f'<h1 class="headline">{esc(article["title"])}</h1>'
            f'<p class="standfirst">{esc(article["standfirst"])}</p>'
            f'<div class="byline">{byline}</div>{tags}</div>'
        )

        if public:
            sections = "".join(f"<div>{render_section(s)}</div>" for s in article["sections"])
            body = f'<article class="article">{head}<div class="article__sections">{sections}</div></article>'
        else:
            # The free portion is a complete thought, not a truncated one: the
            # opening argument, then the boundary. Never a fade, never a blur.
            free = [s for s in article["sections"][:1]]
            shown = "".join(f"<div>{render_section(s)}</div>" for s in free)
            withheld = [d for d in (describe_section(s) for s in article["sections"][1:]) if d]
            items = "".join(f"<li>{esc(d)}</li>" for d in withheld)
            n = len(withheld)
            words = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
                     7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}
            boundary = (
                f'<div class="boundary">'
                f'<div class="eyebrow">The rest of this analysis is for subscribers</div>'
                f'<p class="boundary__lede">{words.get(n, n)} further '
                f'{"section" if n == 1 else "sections"} follow, and this is what each one tests:</p>'
                f"<ol>{items}</ol>"
                f'<div class="boundary__actions"><a href="{self.url("/subscribe/")}">Subscribe</a>'
                f"<span>Already a subscriber? Sign in.</span></div></div>"
            )
            body = (
                f'<article class="article">{head}'
                f'<div class="article__sections">{shown}{boundary}</div></article>'
            )

        return self.page(
            title=article["title"],
            description=article.get("meta_description", article["standfirst"]),
            body=body,
            current=f'/{kind["path"]}/',
            canonical=f'/{kind["path"]}/{article["slug"]}.html',
        )

    # -- index pages --------------------------------------------------------

    def ledger_table(self, articles: list[dict], universe: int, rule: str) -> str:
        rows = ""
        for a in articles:
            kind = self.s["kinds"][a["kind"]]
            series_signal = " class=\"is-signal\"" if a["kind"] in ("special_report", "analysis") else ""
            rows += (
                f"<tr><td>{esc(short_date(a['published_at']))}</td>"
                f"<td{series_signal}>{esc(kind['label'])}</td>"
                f'<td class="ledger__finding"><a href="{self.article_url(a)}">{esc(a["ledger_finding"])}</a></td>'
                f"<td>{esc(a['ledger_evidence'])}</td></tr>"
            )
        if not rows:
            rows = ('<tr><td colspan="4" style="font-family:var(--serif);font-size:15.5px;'
                    'color:var(--ink)">Nothing published in this series yet.</td></tr>')
        k = len(articles)
        return (
            f'<div class="ledger-wrap"><table class="ledger">'
            f'<colgroup><col class="c-date"><col class="c-series"><col><col class="c-evid"></colgroup>'
            f'<thead><tr><th scope="col">Date</th><th scope="col">Series</th>'
            f'<th scope="col">Finding</th><th scope="col">Evidence</th>'
            f'</tr></thead><tbody>{rows}</tbody></table></div>'
            f'<div class="ledger__count">Showing {k} of {universe} published '
            f'{"item" if universe == 1 else "items"} — {rule}.</div>'
        )

    def index_page(self, *, title: str, blurb: list[str], articles: list[dict],
                   rule: str, path: str, label: str) -> str:
        intro = "".join(f"<p>{esc(p)}</p>" for p in blurb)
        body = (
            f'<div class="stack"><div class="intro">'
            f'<div class="head"><span class="head__label">{esc(label)}</span>'
            f'<h1 class="head__title">{esc(title)}</h1></div>{intro}</div>'
            f'<section style="display:flex;flex-direction:column;gap:10px">'
            f'{self.ledger_table(articles, len(self.articles), rule)}</section></div>'
        )
        return self.page(title=title, description=" ".join(strip_tags(p) for p in blurb),
                         body=body, current=path, canonical=path)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "topic"


# ---------------------------------------------------------------------------
# Standing pages
# ---------------------------------------------------------------------------

def data_page(site: Site) -> str:
    release = site.s.get("release_id") or "not stated on this build"
    rows = [
        ("What the figures come from",
         "A read-only, release-pinned view of a curated maritime data lake. Every published figure "
         "is drawn from one pinned release, and the release is named in the folio on the front page."),
        ("Release on this build", release),
        ("Rates", "Modeled from observed inputs across 38 river segments. Out-of-sample mean absolute "
                  "error is $5.27 per ton, rising to $9.44 per ton in drought conditions."),
        ("River conditions", "Lock queues and gauge readings, observed, dated to the day of the reading."),
        ("Grain demand", "USDA Foreign Agricultural Service (FAS) weekly export sales, observed. "
                         "USDA revises prior weeks; figures are carried as first reported."),
        ("Fleet and vessel data", "Census and survey sources run well behind the present. Where a "
                                  "question can only be answered from a stale source, the page says so "
                                  "and dates the figure to the source, not to today."),
        ("Freshness", "A freshness label is not currency. Lag in days is what is reported, because a "
                      "source can be labelled current at a lag of years."),
        ("Evidence classes", "Observed, calculated, modeled, estimated, provisional, inference. "
                             "No sentence blurs two of them."),
    ]
    dl = "".join(f"<dt>{esc(k)}</dt><dd>{v if k == 'Release on this build' else esc(v)}</dd>"
                 for k, v in rows)
    body = (
        f'<div class="stack"><div class="intro">'
        f'<div class="head"><span class="head__label">Data</span>'
        f'<h1 class="head__title">Where every number on this site comes from</h1></div>'
        f"<p>Nothing here is published without a source, a period and an as-of date. "
        f"This page states what the sources are and what each one can and cannot answer.</p>"
        f'<p>Every figure on a page also carries its own documentation box: source, grain, '
        f'what is shown out of what, period, sample size, units, evidence class, uncertainty, '
        f'who built it, and whether the analysis was pre-specified.</p></div>'
        f'<dl class="deflist">{dl}</dl></div>'
    )
    return site.page(title="Data", description="The sources behind every figure published on Tonnage & Trade.",
                     body=body, current="/data/", canonical="/data/")


def method_page(site: Site) -> str:
    rules = [
        ("Headlines state findings",
         "A headline a reader can agree or disagree with. Not “Barge rates update: July 2026” but "
         "“The low-water rate spike came two months early”. The same applies to section heads and to "
         "every row of the ledger."),
        ("Numbers arrive dated",
         "A number in prose carries its interval and its as-of date. A figure with no traceable "
         "provenance is cut, not hedged."),
        ("Evidence classes are named",
         "Observed, modeled, estimated, forecast — named in words, never blurred inside one sentence. "
         "An estimated point is drawn dashed with an open endpoint so no exhibit implies observation."),
        ("The value axis is never cut",
         "Every exhibit runs its value axis from zero. A cut value axis is a lie about the size of a "
         "move. Where that compresses the trace, the printed start and end values carry the precision. "
         "A cut to the time window is stated in the caption."),
        ("Figures name a guarantor",
         "Ten documentation slots, and a named person who stands behind the figure. A figure without "
         "one does not publish."),
        ("What is shown, out of what",
         "Any threshold, rank filter or \"top of\" framing states the display universe — three of "
         "twenty-six segments, and the rule that cut it. A numerator without its denominator is not "
         "published."),
        ("The argument says where it breaks",
         "Every analysis carries a section that names the reading which would falsify it, and the "
         "watch list carries dated calls that can be checked."),
        ("Corrections are logged in place",
         "With the date and what changed. Nothing is silently edited."),
        ("The page reads in greyscale",
         "No signal is carried by colour alone. Red marks the value under discussion, links, and "
         "access flags — never \"bad\"."),
    ]
    dl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rules)
    body = (
        f'<div class="stack"><div class="intro">'
        f'<div class="head"><span class="head__label">Method</span>'
        f'<h1 class="head__title">The rules a page has to pass before it publishes</h1></div>'
        f"<p>These are enforced on every page, not aspirations. Where a page cannot meet one, it says "
        f"so in the open rather than omitting the slot.</p>"
        f'<p>Prose is governed by the house writing guide; form is governed by the Tonnage &amp; Trade '
        f'design language. Both are part of correctness, not taste.</p></div>'
        f'<dl class="deflist">{dl}</dl>'
        f'<div class="stack--tight" style="display:flex;flex-direction:column;gap:10px">'
        f'<div class="head"><span class="head__label">Log</span>'
        f'<h2 class="head__title">Corrections</h2></div>'
        f'<p class="doc">No corrections have been issued. Each one will be listed here with its date, '
        f'the page it affects, and what changed.</p></div></div>'
    )
    return site.page(title="Method", description="The publication rules every Tonnage & Trade page passes before it ships.",
                     body=body, current="/method/", canonical="/method/")


def subscribe_page(site: Site) -> str:
    free = [a for a in site.articles if site.is_public(a)]
    gated = [a for a in site.articles if not site.is_public(a)]
    body = (
        f'<div class="stack"><div class="intro">'
        f'<div class="head"><span class="head__label">Subscribe</span>'
        f'<h1 class="head__title">What a subscription buys, stated exactly</h1></div>'
        f'<p>The Weekly River Note publishes free: the rate nowcast, the binding lock, the grain '
        f'demand read, and a dated watch list. {len(free)} of {len(site.articles)} published items '
        f'are free to read.</p>'
        f'<p>Special reports and analysis are for subscribers. {len(gated)} of '
        f'{len(site.articles)} published items sit behind that boundary today. Each one states, on '
        f'its own page, how many sections remain and what each section tests — so what is being '
        f'bought is a known thing.</p></div>'
        f'<div class="boundary">'
        f'<div class="eyebrow">Sign-up is not open yet</div>'
        f'<p class="boundary__lede">This site does not collect email addresses or payment details '
        f'at present, and no form on it will ask for either. When subscriptions open, the price and '
        f'the terms will be stated on this page before anything is collected.</p>'
        f'<div class="boundary__actions"><span>In the meantime, the free series publishes weekly.</span>'
        f'<a href="{site.url("/river-notes/")}">Read the River Notes</a></div></div></div>'
    )
    return site.page(title="Subscribe", description="What a Tonnage & Trade subscription includes, and what publishes free.",
                     body=body, current="/subscribe/", canonical="/subscribe/")


def not_found_page(site: Site) -> str:
    body = (
        f'<div class="stack"><div class="intro">'
        f'<div class="head"><span class="head__label">404</span>'
        f'<h1 class="head__title">There is no page at this address</h1></div>'
        f'<p>The ledger on the front page lists everything published, newest first, with nothing '
        f'hidden. Start there.</p></div>'
        f'<div class="boundary__actions"><a href="{site.url("/")}">The front page</a>'
        f'<a href="{site.url("/river-notes/")}">River Notes</a>'
        f'<a href="{site.url("/analysis/")}">Analyses</a></div></div>'
    )
    return site.page(title="Not found", description="No page at this address.", body=body)


# ---------------------------------------------------------------------------
# Feed, sitemap, robots
# ---------------------------------------------------------------------------

def atom_feed(site: Site) -> str:
    root = (site.s.get("base_url") or "").rstrip("/")
    updated = rfc3339(site.articles[0]["published_at"]) if site.articles else \
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = ""
    for a in site.articles:
        link = root + site.article_url(a)
        entries += f"""  <entry>
    <title>{esc(a['title'])}</title>
    <link href="{esc(link)}"/>
    <id>{esc(link or a['slug'])}</id>
    <updated>{rfc3339(a['published_at'])}</updated>
    <author><name>{esc(a['byline'])}</name></author>
    <summary>{esc(a['standfirst'])}</summary>
  </entry>
"""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{esc(site.s['name'])}</title>
  <subtitle>{esc(site.s['scope'])}</subtitle>
  <link href="{esc(root + site.url('/feed.xml'))}" rel="self"/>
  <link href="{esc(root + site.url('/'))}"/>
  <id>{esc(root + site.url('/') or site.s['name'])}</id>
  <updated>{updated}</updated>
{entries}</feed>
"""


def sitemap(site: Site, paths: list[str]) -> str:
    root = (site.s.get("base_url") or "").rstrip("/")
    urls = "".join(f"  <url><loc>{esc(root + p)}</loc></url>\n" for p in paths)
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}</urlset>\n")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def load() -> tuple[dict, list[dict]]:
    settings = json.loads((CONTENT / "site.json").read_text())
    articles = [json.loads(p.read_text())
                for p in sorted((CONTENT / "articles").glob("*.json"))]
    articles.sort(key=lambda a: parse_date(a["published_at"]), reverse=True)
    return settings, articles


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"  {path.relative_to(ROOT)}")


def clean() -> None:
    for d in GENERATED_DIRS:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for f in GENERATED_FILES:
        (ROOT / f).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="",
                        help="URL prefix when the site is not served from a domain root, "
                             "e.g. /tonnage for a GitHub project page")
    parser.add_argument("--clean", action="store_true", help="remove generated files first")
    args = parser.parse_args()

    if args.clean:
        clean()

    settings, articles = load()
    site = Site(settings, articles, args.base)

    for a in articles:
        for field in ("ledger_finding", "ledger_evidence", "as_of", "published_at", "byline"):
            if not a.get(field):
                raise SystemExit(f"{a['slug']}: missing required field {field!r}")

    print("Building:")
    paths: list[str] = []

    write(ROOT / "index.html", site.front_page())
    paths.append(site.url("/"))

    for a in articles:
        path = settings["kinds"][a["kind"]]["path"]
        write(ROOT / path / f"{a['slug']}.html", site.article_page(a))
        paths.append(site.article_url(a))

    # Per-kind indexes. "Analyses" gathers everything that is not a River Note.
    for kind, meta in settings["kinds"].items():
        items = [a for a in articles if a["kind"] == kind]
        if kind == "analysis":
            items = [a for a in articles if a["kind"] != "river_note"]
            title, label = "Analyses", "Series"
            blurb = ["Special reports and analysis — longer pieces that test one relationship and "
                     "state what would falsify it.",
                     "Each carries dated, checkable calls and a documentation box on every figure."]
            rule = "every published item that is not a River Note"
        else:
            title, label = meta["plural"], "Series"
            blurb = {
                "river_note": ["The Weekly Inland River Market Note — rate pressure, the binding lock, "
                               "grain demand, and a dated watch list.",
                               "Free to read, published weekly, every figure dated to its source."],
                "special_report": ["Longer reports on a single market or a single company's print.",
                                   "Each states its calls before the event it is calling."],
                "note": ["Short pieces that carry one figure and one reading.",
                         "Published when a number moves enough to be worth a page."],
            }[kind]
            rule = f"every published {meta['label']}"
        write(ROOT / meta["path"] / "index.html",
              site.index_page(title=title, blurb=blurb, articles=items, rule=rule,
                              path=f'/{meta["path"]}/', label=label))
        paths.append(site.url(f'/{meta["path"]}/'))

    # Topics
    topics: dict[str, list[dict]] = {}
    for a in articles:
        for t in a.get("tags", []):
            topics.setdefault(t, []).append(a)

    rows = "".join(
        f'<dt><a href="{site.url("/topics/" + slugify(t) + ".html")}">{esc(t)}</a></dt>'
        f'<dd>{len(v)} published {"item" if len(v) == 1 else "items"}</dd>'
        for t, v in sorted(topics.items())
    )
    body = (f'<div class="stack"><div class="intro">'
            f'<div class="head"><span class="head__label">Topics</span>'
            f'<h1 class="head__title">Every topic covered, and how much sits under each</h1></div>'
            f'<p>A topic earns a page when something published carries it. Counts are honest: '
            f'nothing is listed that has no page behind it.</p></div>'
            f'<dl class="deflist">{rows}</dl></div>')
    write(ROOT / "topics" / "index.html",
          site.page(title="Topics", description="Every topic covered by Tonnage & Trade.",
                    body=body, canonical="/topics/"))
    paths.append(site.url("/topics/"))

    for topic, items in sorted(topics.items()):
        write(ROOT / "topics" / f"{slugify(topic)}.html",
              site.index_page(title=topic, label="Topic",
                              blurb=[f"Everything published under {topic}, newest first."],
                              articles=items, rule=f"every published item tagged {topic}",
                              path="/topics/"))
        paths.append(site.url(f"/topics/{slugify(topic)}.html"))

    for path, page in (("data", data_page(site)), ("method", method_page(site)),
                       ("subscribe", subscribe_page(site))):
        write(ROOT / path / "index.html", page)
        paths.append(site.url(f"/{path}/"))

    write(ROOT / "404.html", not_found_page(site))
    write(ROOT / "feed.xml", atom_feed(site))
    write(ROOT / "sitemap.xml", sitemap(site, paths))

    robots = "User-agent: *\nAllow: /\n"
    if settings.get("base_url"):
        robots += f"Sitemap: {settings['base_url'].rstrip('/')}{site.url('/sitemap.xml')}\n"
    write(ROOT / "robots.txt", robots)

    if not settings.get("release_id"):
        print("\nNote: content/site.json has no release_id, so the folio prints the date alone.")
        print("      Set it from get_release_status before publishing — the design language")
        print("      requires the release id the page was built against.")

    print(f"\nDone. {len(paths)} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
