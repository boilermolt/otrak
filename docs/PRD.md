# OTRAK — Product Brief (v0)

## Problem
Overtime allocation for a large, multi-trade construction project is complex due to:
- Trade-specific collective agreements
- Critical-path priorities
- Multiple work orders and shifts
- Worker preferences and normal work assignments
- Constraints like 10/12 hour shifts, start times, rest windows

## Objectives
1. **Compliance:** enforce trade-specific rules and agreements.
2. **Coverage:** ensure critical-path work is filled first.
3. **Fairness:** distribute overtime equitably within each trade.
4. **Efficiency:** minimize manual coordination and rework.
5. **Explainability:** show why each assignment was made.

## Users
- Overtime coordinator / schedulers
- Foremen / supervisors
- Trade coordinators

## Inputs (draft)
- Worker roster + trade, qualifications, normal work area
- Collective agreement rule set per trade
- Work orders + criticality + location + required skills
- Shift templates + rest rules
- Worker preferences + availability
- Current overtime history + rotation

## Outputs
- Shift assignments by work order
- Ranked candidate lists per shift
- Audit log of rules applied
- Exportable schedule (CSV/PDF)

## Scope (MVP)
- Single project site
- 3–6 trades
- Weekly scheduling window
- Manual override + re-run

## Non-goals (MVP)
- Payroll processing
- Real-time attendance tracking
- Multi-site coordination

## Open Questions
- Will rules be encoded manually or via RAG from contracts?
- What is the final scheduling cadence (daily/weekly)?
- How are exceptions approved and recorded?
