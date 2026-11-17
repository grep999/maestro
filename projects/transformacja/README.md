# TRANSFORMACJA

A historically grounded corporate-control and economic-transition simulation beginning in Poland in 1990.

## Current baseline — 0.4.0 mechanics prototype + historical atlas 0.1.0

This project directory contains a dependency-free JavaScript simulation kernel, browser interface, historical research data, and regression/provenance checks.

- Acquire 25%, 51% or 100% stakes in fictional local businesses.
- Estimate equity value with an explicit five-year DCF proxy and negotiate offers against seller reserve prices.
- Finance purchases with cash and up to 60% illustrative debt.
- Simulate monthly sales, operating costs, payroll, interest, tax, working capital and cash.
- Change price and wage policies; reinvest in productivity and quality.
- Restructure employment with severance and local social consequences.
- Inspect market shares and HHI.
- Browse sourced GUS privatization aggregates and the IMF 1990–September 1996 route series.
- Inspect five source-backed company transactions and eleven research leads with explicit verification status.
- Convert old złoty to new złoty in 1995 at 10,000:1.
- Save/load locally with model-version validation.

This is a playable mechanics prototype, **not yet a historically calibrated simulation**. Initial companies and numerical parameters are fictional/stylized. Historical case records are not purchasable. DCF assumptions are scenario mechanics, not observed historical valuations.

## Run

From this directory:

```bash
npm test
npm run check
python3 scripts/validate_atlas.py
```

Serve `prototype/` with a static HTTP server and open `prototype/index.html`. It imports `src/app.js` and `src/simulation.js` as browser ES modules.

## Research integrity

Never infer a purchase price, stake, buyer, seller, employment effect or causal outcome from brand ownership alone. Every factual transaction must have a date with explicit precision, transaction type, parties, scope, source locator, confidence and uncertainty notes. Distinguish direct acquisition from greenfield investment, indirect control, asset sale, liquidation and later ownership change. Preserve unknown values as null.

## Maestro integration

The project is an adapter under `grep999/maestro/projects/transformacja`; Maestro's core lifecycle and engine remain at repository root. GitHub Copilot code review is configured as an independent review request on PR open/reopen/ready/synchronize events. Copilot must not author the candidate it reviews, self-approve, or advance Maestro workflow state.

## Known verification limitations

The local candidate's last reported run passed 25 tests and syntax/build/provenance checks. Browser-driven interaction QA was not completed (headless Chromium timed out). The current GitHub integration is being assembled file-by-file; do not treat this README as proof that every local project artifact or the local SQLite workflow database has been transferred.
