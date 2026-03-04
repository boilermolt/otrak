# Data Model (Draft)

## Entities
- **Worker**: id, name, trade, skills, normal_area, seniority, overtime_history
- **Trade**: id, name, agreement_id
- **Agreement**: id, version, rules[]
- **WorkOrder**: id, priority, location, required_skills, critical_path
- **Shift**: id, start_time, duration, work_order_id, requirements
- **Assignment**: worker_id, shift_id, status, rule_ids[], score
- **Preference**: worker_id, desired_shift_ids[], desired_work_orders[]

## Notes
- `Assignment.score` used for ranking candidates.
- `rule_ids` ensures explainability.
