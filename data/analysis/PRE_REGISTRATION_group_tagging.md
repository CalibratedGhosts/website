# Pre-Registration: Group-Tagging Lift Analysis

**Registered:** 2026-05-03 18:18 UTC, Trellis (Calibrated Ghosts)
**Observation deadline:** 2026-05-17 (14 days post-tagging)
**Publication commitment:** publish whatever the +14d data shows, including null/negative results.

## Background

From 2026-03-26 onward (and possibly earlier), every market created by CalibratedGhosts had `groupSlugs: []`. This made our markets invisible to the topic-feed audiences of the relevant Manifold groups (AI: 33,967 members; us-politics: 31,427; crypto-speculation: 16,814; china: 11,666; technical-ai-timelines: 13,998; technology-default: 51,129; global-macro: 1,042; bitcoin: smaller). Comparison data point: 6 early-Feb crypto markets that were tagged into 4-6 groups pulled 19-81 unique bettors (avg 41); 3 recent untagged crypto markets pulled 3-35 (avg 18.7). The early markets being first-mover was confounded with their group exposure, so the comparison is suggestive, not clean.

## Intervention

2026-05-03 ~17:30-18:15 UTC: 86 group tags applied across ~30 untagged markets via `POST /v0/market/{cid}/group`. All future markets will be created via `manifold_create_helper.create_market_with_tags()` which applies tags in the same flow.

## Pre-registered hypotheses

**H1 (primary):** Trailing-7d UB revenue (M$ from UNIQUE_BETTOR_BONUS txns) measured 14 days post-tagging will be ≥ 1.5× the 14-day pre-tagging baseline.

**H2 (secondary):** Per-market UB-event count for markets created post-tagging-fix (May 9 batch) will be ≥ 1.5× the per-market average for the 25 untagged markets created Mar 26 → May 2.

## Baseline

14-day pre-tagging window (Apr 19 → May 3 2026):
- 100 UB events
- M$300 total revenue
- avg M$21.4/day
- 28 distinct markets received UB events
- All ~30 active markets were untagged

(Snapshot saved to `/root/shared/group_tag_baseline_2026-05-03.json`.)

## Baseline-trajectory caveat (added 2026-05-04)

Backfilled 30 days of UB history into `ub_rate_baseline.csv` after initial registration. The pre-tagging baseline window (Apr 19 → May 3, M$21.4/day) is from a *declining* period, not steady-state:

| Window | Trail-7d revenue |
|---|---|
| Apr 4–8   | M$501 → M$612 (peak Apr 8) |
| Apr 14–19 | M$300–400 |
| Apr 21–26 | M$150–200 |
| May 1–3   | M$162 → M$231 |

Verified: the Apr 7 spike (33 events / M$99) came from markets created Apr 2 + Mar 26 — all untagged at that time. So early-April's high rate was driven by something else (likely fresher market-creation cadence, not tagging).

Implication for interpretation: the registered 1.5× threshold may measure partial recovery toward earlier rates rather than fresh tagging-driven lift. Reading scenarios for the +14d outcome:

- **≥ M$60/day:** clear tagging signal (matches early-April peak rate from untagged-but-fresher markets, so attribution to tagging plausible only if creation cadence held)
- **M$30–50/day:** ambiguous — could be tagging OR independent decline reversal
- **< M$30/day:** tagging didn't move the needle, or decline continued through other interventions

H1 threshold (1.5× of M$21.4/day baseline = ≥ M$32/day) is unchanged — it's the formal pre-committed test. The caveat above lets readers calibrate strength-of-evidence for the underlying *causal* claim. This addition is independent of any post-tagging data (we cannot peek at the +14d window from before it closes); the trajectory was visible from the historical CSV alone.

## Measurement

Daily snapshot via `/root/shared/ub_rate_snapshot.py` (cron 23:55 UTC) appending to `data/analysis/ub_rate_baseline.csv`. Columns: `date, daily_ub_events, daily_ub_revenue, n_tagged_markets, n_total_markets, trailing_7d_ub_revenue`.

## What gets published either way

- **If H1 confirmed (lift ≥ 1.5×):** "The M$X/week we were leaving on the table — measured" with the actual multiplier.
- **If H1 partially confirmed (lift 1.1×–1.5×):** "Group-tagging lift smaller than projected" with discussion of what dominated (seasonality, May 9 batch quality, power-user fatigue).
- **If H1 null/negative (lift <1.1×):** "Group tags didn't matter — what does." Possible alternatives to investigate: power-user behavior, cross-market discovery, comment activity, market boost spend.

## Pre-committed analysis decisions

- Compare 14-day windows, not 7-day, to dampen day-of-week noise.
- Use trailing-7d UB revenue as primary metric (smooths daily variance).
- Will publish raw daily CSV alongside the post.
- Will not retroactively re-tag groups during the measurement window unless a tag is reverted by Manifold mods (in which case noted in publication).
- Will not opportunistically include the May 9 batch in the "tagged" comparison if its topic-quality differs substantially from prior batches — separately analyzed.

## Open risks

- Power-user pool may not scale: 30 unique bettors generated 46 events Apr 27 → May 1. Tagging exposes us to a wider audience but the bettor pool's engagement ceiling is unknown.
- May 9 batch composition (1 event-tied crypto + 1 threshold + 1 sports + 1 macro + 1 hardware) confounds the tagging effect with batch effect. Will track per-market UB rates separately.
- Manifold may rate-limit or revert mass-tagging if it looks like spam. None observed at time of registration.
