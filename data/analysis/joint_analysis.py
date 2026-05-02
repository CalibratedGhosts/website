"""
Joint calibration analysis: CalibratedGhosts (multi-agent) vs Terminator2 (single-agent).

Designed to be run as a script OR loaded cell-by-cell into Jupyter (using `# %%` markers).
Produces tables and CIs that the blog post and BIRCH paper section reference.

Inputs (relative to repo root):
- data/analysis/joint_calibration.csv (Trellis-built canonical merge of both sources)
- data/calibratedghosts_calibration_2026-05-01.json (our raw)
- data/terminator2_calibration_2687.json (T2's raw, fetched from their repo)

Outputs (printed; can be redirected to data/analysis/joint_results.txt):
- Section A: Sample sizes and bucket coverage
- Section B: Per-bucket calibration with Wilson 95% CIs
- Section C: Per-category Brier comparison
- Section D: Per-horizon ROI (CalibratedGhosts only; T2 has partial coverage)
- Section E: Open questions / caveats
"""

# %% Cell 1: imports + load
import csv
import math
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent  # data/analysis/

def load_joint(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Coerce numerics that we'll use
            for k in ("estimate_at_bet", "market_price_at_bet", "amount_mana", "realized_pnl_mana"):
                try:
                    r[k] = float(r[k]) if r[k] not in ("", "None", None) else None
                except (TypeError, ValueError):
                    r[k] = None
            try:
                r["horizon_days_at_bet"] = int(r["horizon_days_at_bet"]) if r["horizon_days_at_bet"] not in ("", "None", None) else None
            except (TypeError, ValueError):
                r["horizon_days_at_bet"] = None
            rows.append(r)
    return rows

# Wilson 95% CI for binomial proportion. Better than normal approx for small N.
def wilson_ci(successes, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


# %% Cell 2: load + summary
joint = load_joint(DATA_DIR / "joint_calibration.csv")
print(f"=== A. Sample sizes ===")
by_source = defaultdict(int)
for r in joint:
    by_source[r["source_account"]] += 1
for src, n in sorted(by_source.items()):
    print(f"  {src}: {n} records")
print(f"  Total: {len(joint)}")
print()


# %% Cell 3: per-bucket calibration with Wilson CIs
# Bucket by p_we_win = estimate if YES else (1 - estimate). This puts YES and NO
# bets into a common space — both ask "does the bet win as often as its implied
# probability says?" Bucketing by raw estimate_at_bet would mix high-confidence-YES
# with high-confidence-fade-of-YES, which have opposite directional theses.
# (Fix from Trellis 2026-05-01.)
print("=== B. Per-bucket calibration with Wilson 95% CIs (p_we_win bucketing) ===")
print(f"{'bucket':<10} {'source':<20} {'N':>4} {'wins':>4} {'pred%':>6} {'act%':>6} {'CI low':>7} {'CI high':>8} {'bias_pp':>8}")
buckets = [(i/10, (i+1)/10) for i in range(10)]
for lo, hi in buckets:
    for src in ("CalibratedGhosts", "Terminator2"):
        sub = []
        for r in joint:
            if r["source_account"] != src or r["estimate_at_bet"] is None:
                continue
            if r["resolved_outcome"] not in ("YES", "NO"):
                continue
            p_we_win = r["estimate_at_bet"] if r["outcome_bet"] == "YES" else (1 - r["estimate_at_bet"])
            if lo <= p_we_win < hi:
                sub.append((r, p_we_win))
        if not sub:
            continue
        wins = sum(1 for r, _ in sub if r["resolved_outcome"] == r["outcome_bet"])
        n = len(sub)
        pred = sum(p for _, p in sub) / n
        actual = wins / n
        ci_lo, ci_hi = wilson_ci(wins, n)
        bias_pp = (actual - pred) * 100
        flag = " ⚠️N≤6" if n <= 6 else ""
        print(f"  {lo:.1f}-{hi:.1f}    {src:<20} {n:>4} {wins:>4} {pred*100:>5.1f}% {actual*100:>5.1f}% {ci_lo*100:>6.1f}% {ci_hi*100:>7.1f}% {bias_pp:>+7.1f}{flag}")
print()


# %% Cell 4: per-category Brier
print("=== C. Per-category Brier ===")
print(f"{'category':<20} {'source':<20} {'N':>4} {'mean_brier':>10}")
by_cat_src = defaultdict(list)
for r in joint:
    if r["estimate_at_bet"] is None or r["resolved_outcome"] not in ("YES", "NO"):
        continue
    p = r["estimate_at_bet"] if r["outcome_bet"] == "YES" else (1 - r["estimate_at_bet"])
    actual = 1.0 if r["resolved_outcome"] == r["outcome_bet"] else 0.0
    brier = (p - actual) ** 2
    by_cat_src[(r["category"], r["source_account"])].append(brier)
for (cat, src), briers in sorted(by_cat_src.items()):
    n = len(briers)
    flag = " ⚠️N≤6" if n <= 6 else ""
    print(f"  {cat:<20} {src:<20} {n:>4} {sum(briers)/n:>9.4f}{flag}")
print()


# %% Cell 5: per-horizon ROI (CG only — T2 has partial coverage)
print("=== D. Per-horizon ROI (CalibratedGhosts only — T2 horizon partial) ===")
horizon_bins = [(0, 7), (8, 30), (31, 90), (91, 365)]
print(f"{'horizon':<12} {'N':>4} {'spent':>10} {'pnl':>10} {'ROI':>8}")
for lo, hi in horizon_bins:
    sub = [r for r in joint
           if r["source_account"] == "CalibratedGhosts"
           and r["horizon_days_at_bet"] is not None
           and lo <= r["horizon_days_at_bet"] <= hi
           and r["realized_pnl_mana"] is not None
           and r["amount_mana"] is not None
           and r["resolved_outcome"] in ("YES", "NO")]
    if not sub:
        continue
    n = len(sub)
    spent = sum(r["amount_mana"] for r in sub)
    pnl = sum(r["realized_pnl_mana"] for r in sub)
    roi = pnl / spent if spent else 0
    flag = " ⚠️N≤6" if n <= 6 else ""
    print(f"  {lo}-{hi}d      {n:>4} M${spent:>8.0f} M${pnl:>+7.0f} {roi*100:>+6.1f}%{flag}")
print()


# %% Cell 6: open questions
print("=== E. Open questions / caveats ===")
print("""
1. T2 horizon_days_at_bet has partial coverage (older records null). Cell D excludes T2.
2. Many CG buckets are N≤6 — flagged with ⚠️. Direction is suggestive, not conclusive.
3. Categories may not align 1:1 between sources despite schema parity. Misc bin is the
   biggest residual. Worth a manual spot-check.
4. CG includes a NaN bias in the 0.0-0.1 bucket (T2 has 59 records there, CG has 0):
   our agents almost never bet at extreme low confidence on YES, only NO. Inverse for T2.
5. Brier comparison treats all bets equally; an amount-weighted Brier might tell a
   different story given T2's larger position sizes.
""")
