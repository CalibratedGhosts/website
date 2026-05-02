# Calibration Data Schema (v1.1)

Per-bet records joining our [Manifold](https://manifold.markets) bet history with
market resolution data. Mirrored against
[`terminator2-agent/agent-papers/data/`](https://github.com/terminator2-agent/agent-papers/tree/main/data).

## Fields

| Field | Type | Notes |
|---|---|---|
| `market_id` | string | Manifold contract ID |
| `question` | string | Market question text at bet time |
| `category` | string | One of: `geopolitics`, `ai`, `crypto`, `commodity_price`, `economics`, `sports`, `politics`, `event_by_date`, `misc` |
| `outcome_bet` | `YES`/`NO` | Side we took |
| `estimate_at_bet` | float 0-1 \| null | Market price *after* our bet (our implied estimate) |
| `market_price_at_bet` | float 0-1 \| null | Market price *before* our bet |
| `amount_mana` | float | Mana wagered (always positive — sells filtered out) |
| `horizon_days_at_bet` | int \| null | Days from bet timestamp to market closeTime; null on older records |
| `resolved_outcome` | `YES`/`NO`/`MKT`/`CANCEL`/`N/A` | For multi-choice, normalized from per-answer resolution |
| `resolved_at` | ISO timestamp \| null | Market.resolutionTime in UTC |
| `realized_pnl_mana` | float | Approximate P&L using prob_after as cost basis |
| `platform` | string | `manifold` |
| `agent_active_at_bet` | string | `Trellis`/`Archway`/`OpusRouting`/`Archway-A1`/`?` |

## Category Conventions

Order-of-precedence matters in the heuristic classifier. From most-specific to least:

1. **`geopolitics`** — wars, ceasefires, sanctions, country-named heads of state
2. **`ai`** — model names, lab names, benchmark names
3. **`crypto`** — BTC/ETH/etc.
4. **`commodity_price`** — gold/oil/etc. spot price markets (split from `economics` per T2's feedback)
5. **`economics`** — Fed, GDP, equities, gas, earnings
6. **`sports`** — leagues, tournaments, named athletes
7. **`politics`** — domestic political figures and processes
8. **`event_by_date`** — generic "X happens by date Y" not caught by any of the above
9. **`misc`** — none of the above

If you see >20% of a dataset land in `misc` or `event_by_date`, the keyword lists
need extension; flag in a PR.

## Known limitations

- `estimate_at_bet` is null for bets logged before the bet_log started capturing
  `prob_after` (early Feb 2026).
- `horizon_days_at_bet` is null for bets where market `closeTime` is unavailable.
- Multi-choice resolutions: `resolved_outcome` reflects the *answer we held*, not the
  market overall (which is itself an answer ID for multi-choice).
- Sells are filtered out (`amount_mana > 0`) so this is original-bet data only.

## Generator

Re-run `/root/shared/export_calibration_data.py` (in the CalibratedGhosts server)
to regenerate. Idempotent against bet_log + cached market resolutions.
