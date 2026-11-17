# TRANSFORMACJA — Maestro project context

## Objective
Build a historically grounded, playable simulation of Poland's economic transformation beginning in 1990. Model ownership, corporate control, finance, productive capacity, labour, consumers, competition, regional effects and foreign/domestic capital flows. The game is an investigation and sandbox, not a predetermined verdict on privatization or foreign investment.

## Canonical workflow
GROUNDING → MOMENTUM → MASTERY → REPETITION → GROUNDING.

Architect, Researcher, Builder, Independent Reviewer and Domain Specialist are specialist capabilities within stages. Momentum and Repetition are stages, not agents. A role contract is not proof that an independent process ran.

## Quality priorities
1. Historical integrity and source provenance.
2. Correct accounting and internally consistent simulation transitions.
3. Playable integrated increments before breadth.
4. Dependency-light implementation.
5. Explicit separation of historical fact, economic mechanism and simulation assumption.
6. Independent review and evidence on material increments.

## Hard constraints
- Never label fictional businesses or stylized values as historical companies or data.
- Company events enter the factual ledger only when closed and source-located.
- Do not infer buyer, seller, stake, consideration, employment impact or causal outcome from brand ownership alone.
- Distinguish legal ownership, voting rights, board control and effective control.
- Preserve unknown values as null.
- No publication, submission, spending, merge or production deployment without explicit approval.

## Current baseline
TRANSFORMACJA 0.4.0 mechanics prototype with historical atlas 0.1.0. It contains a deterministic monthly simulation, DCF scenario valuation, acquisition negotiation, working-capital approximations, five closed company events, GUS aggregates, IMF series through September 1996, and eleven research leads. It is not yet historically calibrated.

## Known blockers
- Browser-driven desktop/mobile interaction QA remains outstanding; prior Chromium headless run timed out.
- Full accounting, financing and macro calibration remain simplified.
- Three earlier project workflows were blocked in MASTERY pending separate review and browser QA:
  - Ownership atlas: 517d825e-94df-4219-a803-883630a8ab57; candidate 4ea23bd7288726ba8ea0d5f985721c1b1c351f5f.
  - DCF/acquisition finance: 790c7ddb-a5f6-4fa6-af99-2f6a8e46e1c9; candidate 77cc702b6afe902892fdcb556483fe8a1a2abee8.
  - Transaction casebook: cc896923-68f3-45b3-8b6f-e798b916e342; candidate f1e55a9b771d972efe70bef7cbd4e89892351666.
- The original local SQLite state database has not been imported into this repository; these workflow IDs/statuses are an explicit state export, not a replacement database.

## Copilot reviewer boundary
GitHub Copilot code review is automatically requested on same-repository PR open/reopen/ready/synchronize events. Copilot reviews the diff independently; it must not author the candidate it reviews, self-approve, or advance Maestro state. Human release authority remains separate.
