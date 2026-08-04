# Writing Style

<!-- ORIENTATION — this copy lives in the publishing project, not the data repo.
     There is no linter here; enforcement is the `publishing-checks` skill. References below to
     `reporting/river_notes/CLAUDE.md` and `../outputs/` point at the data repo
     (/Users/beegle/code/tonnage-and-trade/db) — the river-note guide is being rewritten fresh here and
     past editions live there. The Audience split section is local to this copy; preserve it on any
     re-sync. Everything else applies verbatim. -->

Canonical rules for prose generated in this project — analysis, reports, docs, summaries, READMEs,
commit and PR text. Not for code itself. Follow these by default; the user overrides only by saying
so. This is the single source of truth **for prose**; medium-specific guides (the Weekly River Note
in `reporting/river_notes/CLAUDE.md`, the Barge Lines report series in `../outputs/`) extend it with
formatting conventions but do not restate or contradict it.

**Companion — the `visual-style` skill.** This file governs *words*; the `visual-style` skill is the
source of truth for *visual/data display* — layout, charts, tables, list construction, typography
tokens, and color (the house **Warm Paper** palette), plus image-export specs. The two interlock:
where they touch (headlines carry the finding; a sentence usually beats bullets; boring is good; cite
every number), this file governs the wording and `visual-style` governs the form. Any display in a
report obeys both.

## Agent contract — read this first

The rules below are the rationale and full reference. Automated writers use this shorter contract on
every task. The machine-readable companion is [`writing_rules.yml`](writing_rules.yml).

**MUST**

- Identify the deliverable type and audience before drafting.
- State the reader's useful answer in the title and opening; analytical writing must promise a
  decision benefit, not a promotional benefit.
- Lead with the supported finding, consequence, or requested action. If the evidence is inconclusive,
  say that instead of manufacturing a thesis.
- Follow each major claim with the facts that make it true and the decision those facts change.
- Preserve the distinction between observed, calculated, estimated, provisional, inferred, and
  speculative claims.
- Attach traceable provenance to every published number, including its period or as-of date.
- Use the required structure and citation form in the deliverable matrix below.
- Leave an explicit `[UNSOURCED — do not publish]` marker when a required source is absent.
- Run the `publishing-checks` skill before returning publication-ready prose. This project has no
  preflight script; that skill is the check.

**MUST NOT**

- Invent evidence, precision, attribution, or certainty to complete a template.
- Hide model output behind observational language.
- Use a banned opener, measurable adjective without its quantity, internal identifier in
  reader-facing prose, or unexplained acronym.
- Apply a medium-specific convention to a deliverable for which it is not required.

**SHOULD**

- Draft from a structured evidence bundle, verify provenance, then edit for style.
- Draft at least 10 private alternatives for a report title or other high-stakes headline, then
  select the most specific, useful, supportable version. Do not publish the candidate list.
- Prefer one argument and the smallest amount of prose that proves it.
- Include the strongest material caveat or counterargument in analytical work.

**MAY**

- Break a rule when the user, medium, quotation, or source terminology requires it. Record the
  exception in a comment alongside the work; do not silently weaken the global rule.

## Default editorial voice — factual persuasion

All project reports use **Ogilvy-inspired factual persuasion** by default. This means adopting the
craft principles associated with David Ogilvy — research before rhetoric, informative headlines,
reader self-interest, specific proof, and reason-why explanation — without imitating his syntax,
quotations, period mannerisms, or advertising persona.

- **Promise a useful answer.** A report headline tells the intended reader what decision, risk, or
  opportunity the evidence will clarify. The promise must be narrower than the evidence or equal to
  it, never larger.
- **Lead with the most arresting supported fact.** Prefer a named entity, date, amount, rate, or
  contrast to an abstract category. Interest comes from specificity, not hype.
- **Give the reason why.** Build every major section as reader-relevant headline → evidence → why the
  evidence produces the conclusion → decision or monitoring implication → disproof or caveat when
  material.
- **Respect the reader.** Write to one intelligent operator, lender or insurer.
  Do not flatter, scold, sensationalize, or conceal uncertainty.
- **Let useful copy run.** Long copy is acceptable when each paragraph adds proof, explanation, or
  decision value. Cut it when it merely repeats the thesis.
- **End with an assignment.** Tell the reader what to record, compare, ask, approve, reject, or watch
  next. In an analytical report, this is the equivalent of a call to action.

For this project, "benefit" means decision usefulness. The goal is not to sell Kirby, Tonnage &amp;
Trade, a security, or a transaction. The goal is to make sourced industry evidence more memorable
and actionable.

## The directives

1. **One thesis, stated first.** Open with the finding or the claim, never the setup. The first
   sentence is the conclusion; the rest earns it. Never open with "This report examines…" or a
   restatement of the prompt.

2. **Headlines carry the point.** Every title, section heading, and chart caption states the
   finding, not the topic. Not "Q2 Barge Rates" → "Tank barge rates broke the 2022 high in Q2." Not
   "Figure 3: Rates 2020–2026" → "Figure 3: Rates now exceed the 2022 peak." (For chart captions,
   figure titles, and exported-image headlines, the `visual-style` skill makes this concrete — see its
   `references/charts.md` §4.4 and `references/exports.md` §10.)

3. **Replace adjectives with numbers.** Never characterize a magnitude you can quantify. Strip the
   intensifier and supply the measured quantity; let the reader judge whether it's "significant."
   - Not "margins improved meaningfully" → "gross margin went from 18% to 26% in three quarters."

4. **Cite every number.** No quantitative claim ships without a traceable source — figure, date,
   origin. If you can't source it, flag it as an estimate or cut it. Never invent a precise-sounding
   statistic to fill a gap.

5. **Separate fact, inference, and speculation — and say which is which.** "Rates rose 31%" (fact)
   and "which suggests restocking" (inference) are different kinds of statement. When uncertain,
   state confidence and what would change the conclusion. A flagged guess is useful; a disguised one
   destroys trust.

6. **State the counterargument.** Give the strongest opposing case, fairly, before the reader thinks
   of it. Don't present one side as if the other doesn't exist.

7. **Show, don't claim.** Prefer a table, comparison, or worked example over an assertion. Caption
   every exhibit with its conclusion, not its contents. (Build the table/chart/exhibit itself per
   the `visual-style` skill — `references/charts.md` §4 and `references/tables-lists-type.md` §6.)

8. **Cut anything that doesn't strengthen the argument.** Length is earned by relevance, not by
   thoroughness for its own sake. Before finishing, remove every sentence whose deletion wouldn't
   weaken the point.

9. **Plain language, precise terms.** Short words, short sentences, short paragraphs. Use domain
   terms where they carry real meaning (a *hopper barge* is not a *tank barge*); never use jargon as
   decoration. Spell out acronyms on first use. The reader should need a glossary to check your
   facts, never to follow your reasoning.

10. **Make the takeaway unmistakable.** End knowing exactly what the reader should now believe or do.
    If the deliverable has an ask, state it plainly.

## Banned openers (throat-clearing — delete, say the thing)

An opener that announces the subject instead of stating it wastes the one sentence a skeptical reader
is guaranteed to read. Delete it and lead with the finding. The most common: *"It is worth noting
that…"*, *"This report examines…"*, *"In today's fast-paced…"*, *"Needless to say."*

**Complete list: `writing_rules.yml` → `banned_openers`.** That file is canonical; add terms there.
The rule catches these after a heading or a bullet marker too, not only at the start of a paragraph.

## Banned adjectives (require a number instead)

When an adjective characterizes something you could measure, it is standing in for the number and
costs the reader the evidence: *strong, significant, substantial, dramatic, sharp* and their kin. If
you reach for one, write the quantity that earned it. The test is the sentence, not the word —
"elevated," "firm" and "easing" are fine when a number sits next to them, and a measurable adjective
in a sentence that already carries its quantity is not a violation.

**Complete list: `writing_rules.yml` → `measurable_adjectives`.**

## AI tells to avoid

These mark text as machine-generated and violate the "no decoration" rule. The vocabulary items —
filler verbs and nouns like *delve, tapestry, realm, navigate, underscore, showcase, foster,
testament to*, and hedge-stacks like *may potentially* — are enumerated in **`writing_rules.yml` →
`ai_tells`**, which is canonical.

The structural tells have no list to check, so they are stated here in full:

- The **"not just X, it's Y"** construction, in any variation.
- The **reflexive rule-of-three** ("fast, reliable, and scalable"). Three items are fine only when all
  three are load-bearing and distinct.
- **Vague quantifiers** — *several, various, a number of, some* — when an actual count is available.
  Give the count.
- **Summary paragraphs** that restate what was just said. End on the last real point.
- **Over-bolding and over-bulleting** prose that should be sentences. Bold the numbers that moved, not
  the topic sentence of every paragraph. When a list *should* exist, build it per the visual guide's
  list rules — substantive order, no 7-item cap, no bullet crutch, domain and date stated.

## Commit messages and PR descriptions

Same discipline, compressed. Subject line states what changed and why it matters, in the imperative
("Add retry to fax sender after Telnyx 5xx"), not what files moved. Body explains the *why* and any
non-obvious tradeoff — never narrate the diff. Lead with the consequence.

## The test

Read the draft as the skeptical reader it's for. Does line one give the point? Is every magnitude a
number with a source? Could any paragraph be cut without loss? Does it sound like a person who knows
the subject, or like a template? Fix whatever fails before returning it.

## Deliverable contracts

Agents select one contract before drafting. A component is required only where the table says it is;
for example, a counterargument belongs in an analysis but not in a one-line commit subject.

| Deliverable | Required sequence | Citation form | Completion test |
|---|---|---|---|
| Market analysis or report | Finding → evidence → interpretation → material counterargument/caveat → takeaway | Inline source name plus period/as-of date; link or exhibit ID where available | Reader knows what changed, why it may matter, what could disprove it, and what to do |
| Weekly River Note | Subject-line finding → weekly changes → implications → bottom line | Source line per panel/table; as-of date on every figure | All published sections passed the report gate and suppressed evidence is absent |
| Chart title/caption | Finding → period and unit → source/as-of date | Documentation box defined in the `visual-style` skill | Caption still makes sense when separated from surrounding prose |
| README or operating doc | Purpose → use → constraints → verification | Link to authoritative local file or external source | A new operator can complete and verify the task |
| Commit | Imperative consequence | Normally none; issue/reference when material | Subject says what changed and why it matters |
| PR description | Outcome → motivation → validation → risks/tradeoffs | Links to issue, evidence, or test output where useful | Reviewer can judge behavior and risk without narrating the diff |

## Audience split — applies to every report

<!-- Local to this project. Not present in db/docs/writing_style.md; preserve it if this file is
     ever re-synced from there. -->

One body of verified analysis, decomposed by reader class. This is structural, not a matter of tone:
the evidence is identical across audiences and only the decision changes.

**The rule.** Before drafting, name the reader classes the evidence actually reaches — from the set
the directives establish — **operator, lender, insurer**. For each one, state the decision the finding
changes. Those three are the set because they are the readers whose decisions this evidence has actually
changed in shipped work; adding a fourth class means first naming the decision it owns. Then write to those decisions, not to a general reader.

- **A class earns a section only if the evidence changes a decision it owns.** If you cannot name the
  decision, cut the class. Three real audiences beat five padded ones, and a padded audience section
  is where overreach enters — it forces a claim the evidence does not carry.
- **Never restate the analysis per audience.** Establish each finding once, then say what it means for
  each reader. An audience section that re-argues the finding is a summary paragraph in disguise.
- **The decisions must differ.** If two classes would do the same thing, they are one audience. The
  operator adjusts a rate floor or a fuel hedge; the insurer reprices a peril or a book; the lender
  revisits a covenant or a collateral value. Same number, three different actions.
- **Scope each read to what that reader can act on.** A lender cannot act on a lock wait time; it can
  act on what the wait implies for a borrower's cash conversion.

**In a single report.** Establish the finding, then carry the audience reads in the interpretation and
takeaway positions of the market-analysis contract above. The counterargument stays global — it
belongs to the evidence, not to any one reader, and it is not to be softened per audience.

**Across a series.** One post per audience after a lead post that establishes the finding. The lead
carries the full evidence and the counterargument; each audience post restates the finding in one or
two sentences, cites back, and spends its length on the decision. Every post in the series must stand
alone for a reader who never sees the others, which means the source and as-of date travel with every
figure in every post — a citation back to the lead is not provenance.

**The completion test.** For each audience section, a reader in that class can name the thing they
would do differently on Monday. If the answer is "be aware of this," the section is not finished.

## Provenance and uncertainty vocabulary

Use these labels consistently; do not substitute a more confident verb for a weaker evidence class.

| Label | Meaning | Reader-facing pattern |
|---|---|---|
| **Observed** | Directly measured or reported by the named source | “USDA reported…” |
| **Calculated** | Deterministic arithmetic from observed inputs | “Calculated from USDA weekly rows…” |
| **Estimated** | Model output or imputation | “Our estimate from river levels, season and fuel…” |
| **Provisional** | Published value that the source may revise | “The provisional June value…” |
| **Inference** | Interpretation supported, but not directly measured | “This suggests…” followed by the evidence and countercase |
| **Speculation** | Plausible explanation without adequate confirming evidence | “One possibility is…” plus what evidence would confirm it |

When evidence is unavailable or incomplete, use one of these literal markers during drafting:

- `[UNSOURCED — do not publish]`
- `[ESTIMATE — method: <method>; as of: <date>]`
- `[PROVISIONAL — source may revise]`
- `[INCONCLUSIVE — evidence does not distinguish between <A> and <B>]`

An unsourced marker is a publication blocker. The other markers require a method or source and an
as-of date before publication.

Golden before/after examples for openings, inference language, inconclusive findings, estimates,
captions, tables, commits, and PRs live in
[`examples/writing_examples.md`](examples/writing_examples.md). They demonstrate the
rule; they are not fill-in-the-blank claims.

---

## Extensions for market-facing prose (River Note & Barge Lines reports)

The directives above are universal. These formatting conventions apply to reader-facing river/rate
prose — the Weekly River Note and the Barge Lines KEX reports. They are conventions, not new rules.

- **Rate tables:** `$`-prefix every value in a $/ton column *and* its change column (`$20.94`,
  `↓ $0.39`). Title the change column **"Change vs. last week,"** never bare "WoW."
- **Gauges / locations:** plain-English name with the ID in parentheses, then the reading — e.g.
  *"Mississippi River at St. Louis, MO (NWS EADM7) — 22.7 ft stage."* Never publish a bare site ID.
- **Say "river segments," not "reaches,"** in reader-facing text. "Reach" is the USDA/USACE schema
  term; keep it only inside a source line that names the mart.
- **Describe tools and metrics; don't coin a sub-brand for them.** Name a thing by what it is and
  does, not with an invented house label the reader has to learn. The rate model is the running
  example: don't christen it "the nowcast" (or any capitalized in-house brand) — write "our estimate
  of barge rates from river levels, season and fuel," "the modeled rate ($/ton)," "how tight the
  market is." The specific word matters less than the instinct — describe, don't brand. Internal
  identifiers stay internal: DB table names like `mart_rate_nowcast` / `mart_nowcast_run` may appear
  verbatim in a `<code>` source citation for traceability, but the prose around them describes the
  thing. This is directive 9 made concrete.
- **Model-confidence caveat in reader terms, not builder diagnostics.** Lead with the accuracy
  figure — *"on weeks it hasn't seen, the estimate lands within about $5.27/ton of actual, widening
  to ~$9.44/ton in drought"* (from `mart_nowcast_run` out-of-sample MAE). Drop in-sample correlation
  and row counts from reader-facing text.
- **Leading vs lagging demand signals:** label a leading signal as leading and say what it is
  (contract $, permit units), not barge tonnage; hedge lagging quarterly counts with an as-of date.
- **Every figure carries an as-of date**; every exhibit's caption states its conclusion (directive
  7), and each panel carries its own source line.

The house **visual system** — Warm Paper palette, serif-for-prose / sans-for-data type, chart, table
and sparkline defaults, and the image-export specs — lives in the `visual-style` skill; follow it for all
new report visuals. The pieces already published on the site — the KEX / Barge Lines series and the earlier River Notes — ship an older **FT-paper** scheme: salmon `#FFF1E5` background, orange `#FF8833` accent, Georgia serif. Those stay as published. Republishing a piece in a new palette changes the record a reader already saw, and the archive is not worth rewriting. **Warm Paper is the standard for all new work**; the archive is simply older, not pending migration. Never start new work from the FT-paper tokens. The archived Barge Lines / KEX reports also carry conventions this
project has not adopted — numbered sections, posture cards, a dated falsifiable watch list, and Chart.js
rendering; treat those as artifacts of that series, not as house rules.
