# OTRAK — Product Brief (v0)

## Problem
Overtime allocation for a large, multi-trade construction project is complex due to:
- Trade-specific collective agreements
- Critical-path priorities
- Multiple work orders and shifts
- Worker preferences and normal work assignments
- Constraints like 10/12 hour shifts, start times, rest windows

## Objectives
1. **Coverage:** ensure critical-path work is filled first.
2. **Fairness:** distribute overtime equitably across eligible workers.
3. **Qualifications-first:** enforce required certifications/quals for specific jobs.
4. **Efficiency:** minimize manual coordination and rework.
5. **Explainability:** show why each assignment was made.

## Users
- Overtime coordinator / schedulers
- Foremen / supervisors
- Trade coordinators

## Inputs (draft)
- Worker roster + qualifications + normal work area
- Work orders + criticality + location + required qualifications
- Shift templates (10/12 hr, start times)
- Worker preferences + availability
- Current overtime history + rotation (if available)

## Outputs
- Shift assignments by work order
- Ranked candidate lists per shift
- Audit log of rules applied
- Exportable schedule (CSV/PDF)

## Scope (MVP)
- Single project site
- Weekly scheduling window (Tue availability → Wed 8am draft)
- Manual override + re-run
- **Phase 1:** fairness + qualifications only (trade pay rules deferred)

## Non-goals (MVP)
- Payroll processing
- Real-time attendance tracking
- Multi-site coordination

## Open Questions
- Will trade agreement rules be encoded manually or via RAG (Phase 2)?
- What exception categories should be tracked in overrides?
