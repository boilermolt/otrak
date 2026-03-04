# Rules & Constraints (Draft)

## Categories
1. **Trade Agreement Rules**
   - Overtime eligibility windows
   - Seniority/rotation requirements
   - Minimum rest periods
   - Maximum consecutive shifts

2. **Operational Rules**
   - Critical-path work orders filled first
   - Coverage requirements (min staffing)
   - Required skills/certifications
   - Shift templates (10/12 hr, start times)

3. **Preference Rules**
   - Prefer normal work area when possible
   - Respect worker requests if not conflicting

## Rule Representation (Draft)
- `Rule(id, trade, type, condition, constraint, priority, source)`
- Every assignment includes `rule_ids[]` applied.

## RAG vs Manual Encoding
- **Manual encoding** for deterministic rules and easy testing.
- **RAG** only for explanatory context or rule discovery.
