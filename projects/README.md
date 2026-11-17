# Project adapters

This directory is an optional extension point, not the home of Maestro itself.

Each adapter connects Maestro to one independently governed project. It records only the context needed to orchestrate that project: purpose, stakeholders, source-of-truth locations, domain-specific roles, current state, constraints, acceptance rules, risk and approval boundaries.

Project code, product identity, canonical backlog, domain documentation and evidence remain in their own source of truth. Maestro must work with this directory empty.

Start with [PROJECT_ADAPTER_TEMPLATE.md](PROJECT_ADAPTER_TEMPLATE.md).
