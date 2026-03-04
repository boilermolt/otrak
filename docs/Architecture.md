# Architecture (Draft)

## Components
1. **Rules Engine**
   - Evaluates constraints + eligibility
   - Produces ranked candidates per shift

2. **Scheduler**
   - Fills critical-path shifts first
   - Applies fairness rotation + preferences

3. **UI / Admin**
   - Upload rules + rosters
   - Review + override assignments

4. **Audit Layer**
   - Stores applied rules, conflicts, exceptions

## Tech Direction (placeholder)
- Backend: Python or Node service
- Rules: JSON/YAML ruleset with tests
- UI: React or Svelte
- Storage: Postgres + optional sqlite for local
