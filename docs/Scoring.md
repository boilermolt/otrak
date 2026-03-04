# Scoring Model (v0)

## Objective
Rank eligible candidates for each shift so we fill critical-path work first, keep fairness across workers, and respect preferences when possible.

## Eligibility (Hard Filters)
A worker is eligible if:
- availability = Y
- required qualifications satisfied (e.g., class7_shipper)
- (optional) any other hard constraints defined for the shift

> Trade is **not** a hard filter in v0.

## Priority Ordering (Shifts)
1. Critical-path shifts
2. Non‑critical by priority (1–5)
3. Higher headcount first (if tied)

## Base Score
Start at **100**.

## Fairness Weights
- **-1.5 × OT hours last 30 days**
- **-0.1 × OT hours lifetime** (if available)

## Preference Weights
- **+10** if preferred shift matches
- **+5** if preferred area matches
- **+10** if normal_area matches

## Qualification Comfort (Soft)
- **+5** for optional/bonus quals that align with shift

## Penalties
- **-20** if shift type conflicts with stated preference (e.g., “10 only” → 12 hr)

## Assignment
For each shift:
- rank eligible workers by score (desc)
- select top N (headcount)
- record reasons: top 3 scoring factors + rule IDs

## Overrides
Upper management can override assignments. Overrides must include a reason.
