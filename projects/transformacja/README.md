# TRANSFORMACJA — project adapter

**Adapter status:** ACTIVE / integration in progress  
**Project source:** `grep999/maestro`, branch `working`, path `projects/transformacja/`  
**Local candidate at integration time:** `cdb4e352558ce0308e313aeddb7fd1c272e85d07`

TRANSFORMACJA is a historically grounded, playable simulation of Poland's economic transformation beginning in 1990. Its purpose is to model corporate control, privatization routes, finance, productive capacity, labour, consumers, competition, regional effects, and domestic/foreign capital flows without assuming a predetermined verdict.

## Source-of-truth boundary
This directory is the project's integration home in the Maestro repository. The project-specific source, data, tests, docs, build output, and workflow state belong here. Maestro's own engine and canonical workflow remain at repository root and are not replaced by this adapter.

## Current baseline (reported from local candidate)
- Prototype version: 0.4.0.
- Dependency-free browser simulation and standalone HTML build.
- Five company-level transaction events with source provenance; official aggregate series and research leads are separate.
- DCF-based indicative valuation and seller negotiation mechanics are scenario mechanics, not historical valuations.
- Last local verification: 25 tests passed; `npm run check`, `npm run build`, Maestro packet validation, atlas validation, and `git diff --check` passed.
- Browser-driven interaction QA was not completed; Chromium headless timed out.
- Three Maestro workflows remain blocked at MASTERY pending independent review and browser QA.

## Required review posture
Use the `maestro-independent-code-review` skill for review. Copilot is an independent reviewer capability; it must not author the candidate it reviews, self-approve, or advance Maestro workflow state. Findings must be evidence-backed and verdicts must be PASS, CONDITIONAL, FAIL, or BLOCKED.

## Integration note
This adapter is committed before the full local project source transfer. It does not claim that the complete TRANSFORMACJA codebase has been pushed or reviewed.
