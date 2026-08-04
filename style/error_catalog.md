# Error catalog

Every class below either shipped or was caught late on a Tonnage & Trade report. Each entry gives the
real case, how it surfaced, and the check that would have caught it earlier. Read when reviewing a
draft, or when a figure feels too convenient.

Grouped by where the error enters: evidence, reasoning, arithmetic, prose, charts.

---

## Evidence

### A. A research finding's summary line overstates its own numbers

**Case.** A casualty finding's claim read "loss of propulsion rose 8.2 points — four times larger than
any other category shift." Its own `numbers` field listed pollution-referenced at +5.00. The true
multiple is 1.6×. The claim was copied into a report and a LinkedIn article before anyone compared
the two fields.

**Caught by** building a chart of the category shifts, which put +8.16 and +5.00 side by side.

**Check.** For every finding you intend to use, read the `numbers` field against the `claim` field and
confirm the claim is the weakest statement the numbers support. Superlatives ("only," "four times,"
"the one X that") are the highest-risk phrases in any research return, including your own.

### B. An inherited figure that does not reproduce

**Cases.** (1) Average tank-barge age of 19.6 years, carried from a prior edition — reproduces on no
basis: simple mean is 24.3 as of 2026, 21.3 at the census date, median 16.0 or 19.0, capacity-weighted
18.4 or 21.4. (2) The Jones Act waiver commodity list, carried as 671 — every source says 659 for the
March 18, 2026 list. (3) A task premise asserting the lock feed does not observe the Gulf Intracoastal.

**Check.** Re-derive anything you did not compute this session, including figures from memories, prior
editions, and your own task prompts. A number with no derivation this session is a citation to
yourself. Any metric that moves with time carries an explicit as-of year in the sentence.

### C. A "fresh" freshness label that is not currency

**Case.** The USACE vessel census reports `lag_status: fresh` at a 940-day lag, because its declared
cadence budget for an annual census is 1,100 days. Building a 2026 supply argument on it without
saying so would imply current data.

**Check.** Read `lag_days`, never `lag_status` alone. Call `get_release_status` and note which datasets
the release flags stale before planning any query. If a question can only be answered stale, say so in
the limits rather than answering it.

### D. A real quotation that the staged extract could not support

**Case.** A verifier flagged the phrase "higher fuel-related receivables" as unverifiable because the
facts file paraphrased that passage instead of quoting it. The quote was genuine and in the release.

**Check.** Stage quotations verbatim in the evidence bundle, with the sentence around them. A verifier
can only test what it can see, and a false alarm on a real quote costs the same review time as a real
error.

### E. A date from a search summary presented as scheduled fact

**Case.** Genesis Energy's Q2 date came from a search-result synthesis whose returned links were about
a different company. It later verified as August 6 from the company's own investor events page.

**Check.** Any date a reader will diary needs a primary source. Search synthesis is a lead, not a
citation. Where the primary source cannot be reached, publish the caveat in the docbox.

---

## Reasoning

### F. A period chosen because it supports the thesis

**Case.** A working-capital thesis rested on Q2 free cash flow of $0.7M against $22.5M a year earlier.
The same release reported six-month operating cash flow up 30.2% and free cash flow swinging to
+$50.1M from −$19.7M. The debt increase was fully explained by acquisitions plus buybacks without
invoking receivables at all. The claim was killed by all three verification lenses.

**Check.** Before asserting a trend from one period, check the adjacent period in the same document.
If they disagree, disclose both in the same breath or drop the claim. Demote the mechanism to a
diligence test rather than an observed event.

### G. Generalizing from one reporter to an industry

**Case.** A claim that "margin dispersion across the industry widened sharply" rested on one company's
margin. No industry margin distribution existed, and the only same-period peer attributed its own
decline to drydock timing rather than fuel.

**Check.** Name the population the claim covers. With n=1 or n=2, state the mechanism and the test date
instead of the conclusion. "Testable on August 6" is honest; "dispersion widened" is not.

### H. A model residual read as a market signal

**Case.** An observed-minus-modeled rate gap of −$1.36/ton looked like a signal. The model's own
out-of-sample error is $5.26/ton, rising to $9.41 in drought, and a naive benchmark beat it overall.

**Check.** Quote a model's out-of-sample error in the same sentence as any residual derived from it.
If the residual is smaller than the error, it is a description of noise. Lead with the accuracy figure
in reader terms, not with builder diagnostics.

### I. A metric that does not measure what its name implies

**Case.** `rate_pressure_index` correlates 0.917 with the model's own prediction and −0.02 with the
residual — it ranks driver conditions, not market mispricing. It is a full-sample percentile, so its
published history could not have been seen in real time, and its dominant input was frozen at a
May value for three months. It read 57.6 during the worst low-water month in the record.

**Check.** Before using a derived index, correlate it against its candidate inputs, check whether its
ranking is expanding-window or full-sample, and confirm its drivers actually vary over your window.
Then decide whether its name matches its behaviour, and describe it by what it does.

### J. Attributing a cause the source itself did not claim

**Case.** A coastal rate decline was attributed to added vessel availability in an 80,000–100,000 bbl
band. That band holds about 15 barges nationally and the reporting company operates about 8 of them.
No independent source corroborated the added supply.

**Check.** When repeating a company's own causal attribution, state the size of the market it describes
and who holds it. Then label the attribution unverified rather than confirmed.

---

## Arithmetic

### K. A derivation inherited from the source's rounded figures

**Case.** A margin decline published as 370 basis points is the difference of two rounded percentages.
Recomputed on unrounded dollars it is 375.8.

**Check.** Recompute every derived figure from the most precise inputs available, and say which
convention you used when it differs from the source's own.

### L. A shortcut decomposition that is not true

**Case.** "The entire decline sits in one cost line" — cost of sales actually took 423 basis points
against a 376-point net decline, with depreciation and overhead leverage returning the difference. Cost
of sales absorbed *more* than the whole.

**Check.** When components do not sum trivially to the total, state the decomposition. If the shortcut
is worth keeping for readability, make it accurate: "absorbed more than the whole decline."

### M. An extract that does not foot, producing confident false positives

**Case.** A staged marine-segment table omitted SG&A and taxes-other-than-income. A verifier
correctly found it would not reconcile and reported a $43M "undisclosed segment expense line" that
does not exist. Review time went to a phantom.

**Check.** Any financial table staged for verification must reconcile to the reported subtotal. Test
the reconciliation yourself before handing it to anyone.

### N. Percentage points confused with percent

The gap between a 76.9% increase and a 50.3% increase is **26.6 percentage points**. As a proportion it
is 34.6% (retail captures 65.4% of the true growth rate) or 52.9% the other way. Writing "27 percent"
for the first understates the error and is simply a different quantity.

**Check.** Subtraction of two percentages yields percentage points, always. When the audience needs to
feel the size, translate to their unit — on $10M of prior-year fuel spend, that 26.6 pp is a $2.66M
miss, 17.7% over the modeled line — and label the assumed base as illustrative.

---

## Prose

### O. Internal identifiers in reader-facing prose

**Case.** Relation names, column names and row counts appeared in the argument of four articles.
This is a MUST NOT in the prose guide, and the linter does not check it.

**Check.** Schema names live inside a source citation. The prose around them describes the thing.
Keep the originating agency — dropping "Coast Guard" or "Corps of Engineers" implies the house
generated data it only curates.

### P. Unexplained acronyms

**Case.** ULSD, GIWW, ATB, P&I, IMEA and SOFR all reached a draft unexpanded. Also a MUST NOT with
no linter rule.

**Check.** Grep the draft for capitalized runs of three or more letters and confirm each is expanded on
first use. Domain terms that carry real meaning are fine; jargon as decoration is not.

### Q. Jargon that survives because the author knows what it means

**Case.** "Covenant projection" appeared in an operator-facing lede. The reader asked what it meant,
which is the signal it did not belong there.

**Check.** For each term, ask whether *this* article's audience uses it daily. Move audience-specific
mechanics to the article written for that audience.

---

## Charts

### R. Label collisions invisible to preflight

**Case.** Four separate collisions across five charts — a value label over an axis label, a value
label over a category name, an annotation behind a highlighted bar, a callout across a reference line.
Every one had correct geometry.

**Check.** `preflight image` validates dimensions and then asks for manual review. Read every rendered
PNG yourself. Budget this time; it is not optional and it is not automatable today.

### S. A chart headline that argues with its own chart

**Case.** "Machinery failure is the one peril that grew. Everything else barely moved." — printed above
a bar showing pollution-referenced incidents up 5.00 points.

**Check.** After rendering, read the headline against what the chart shows, as a reader who has not
seen the prose. A chart is the last checkpoint before publication and the first place a soft claim
becomes visibly false.

### T. Unsourced points plotted alongside sourced ones

**Case.** A weekly diesel series carried an interpolated first point so the line would start earlier.

**Check.** Plot published values only. State `n` and the period in the docbox, and say explicitly when
every plotted point is a published print.

### U. Provenance that does not survive a screenshot

**Case.** Charts published to a social feed get screenshotted out of their article, taking the caption
and source block with them.

**Check.** Bake source, as-of and the evidence class into the exported card itself. If a line is
estimated rather than observed, the image must say so on its face.
