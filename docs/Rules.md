# Rules & Constraints (Draft)

## Categories
1. **Eligibility (Hard Filters)**
   - Required qualifications/certifications (e.g., Class 7 Shipper)
   - Availability window

2. **Operational Rules**
   - Critical-path work orders filled first
   - Coverage requirements (min staffing)
   - Shift templates (10/12 hr, start times)

3. **Fairness + Preference (Soft Rules)**
   - Weight down workers with high OT totals
   - Prefer normal work area when possible
   - Respect worker requests when feasible

4. **Deferred (Phase 2)**
   - Trade agreement wage rules / pay schedule nuances
   - Trade‑specific eligibility constraints (if any)
   - Contract extraction pipeline: `chunks -> contract_facts (reviewed) -> generated agreement rules`

## Rule Representation (Draft)
- `Rule(id, type, condition, effect, weight, source)`
- Every assignment includes `rule_ids[]` applied.

## RAG vs Manual Encoding
- **Phase 1:** manual encoding for deterministic rules + easy testing.
- **Phase 2:** optional RAG for agreement discovery / interpretation.
