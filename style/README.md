# House style

`writing_style.md` explains the prose system; the `visual-style` skill covers everything visual. The
YAML files hold the enumerable rules so a single lookup does not mean re-reading the guide.

Which file owns which rule is stated once, in the project `CLAUDE.md`. Do not restate it here.

| File | Authority |
|---|---|
| `writing_style.md` | Full prose rationale and project-specific application, including the audience-split rule |
| `writing_rules.yml` | Prose rules as structured data: openers, AI tells, terminology, deliverable contracts |
| the `visual-style` skill | Authority for everything visual — palette, charts, tables, lists, integrity tiers, exports. Lives at `.claude/skills/visual-style/`, with deep sections in its `references/` |
| `chart_rules.yml` | Chart contract, display selection, integrity tiers, export presets |
| `visual_tokens.css` | Canonical color, typography, spacing, and sizing tokens |
| `components.css` | Tables, documentation boxes, chart shells, responsive defaults. Inline it — never link it |
| `examples/` | Golden prose examples and a valid chart specification |
| `error_catalog.md` | Error classes that have already shipped on this series, with the case and the check |

## Workflow

1. Name the deliverable and its audiences; select a prose contract, or write a chart specification.
2. Verify evidence class, provenance, period, units, and as-of date for every figure.
3. Draft against the contract; build charts from the verified figures.
4. Run the `publishing-checks` skill — it is the enforcement mechanism here. There is no preflight
   script in this project; the checks are performed by reading the draft.
5. Render the HTML and look at every image. Label collisions, font substitution, and a headline that
   contradicts its own chart are invisible to any rule.
6. Re-read against the guides' own test: does line one give the point, is every magnitude a number with
   a source, could any paragraph be cut without loss.

Read the guides themselves, not only the YAML.
