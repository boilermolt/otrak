# OTRAK

**Overtime & Trade Rules/Allocation Kernel**

OTRAK is a management tool for distributing overtime across a large construction workforce (~200 people) with multiple trades, collective agreements, and complex scheduling constraints.

## Goals
- Allocate overtime fairly and compliantly across trade-specific agreements.
- Prioritize critical-path work orders and coverage needs.
- Respect shift rules (10/12 hour, start times, rotation, rest windows).
- Support worker preferences while keeping operations efficient.
- Produce auditable decisions (who, why, and which rules applied).

## Core Ideas
- **Rules-first**: trade-specific contract rules are explicit and testable.
- **Priority-aware**: critical-path coverage comes before discretionary fills.
- **Preference-aware**: try to place workers in their usual roles when possible.
- **Explainable**: every assignment records the rules and constraints used.

## Docs
- [Product brief](docs/PRD.md)
- [Rules & constraints](docs/Rules.md)
- [Data model](docs/Data-Model.md)
- [System architecture](docs/Architecture.md)

## Status
- Scaffolded. Next step: confirm scope + data inputs.
