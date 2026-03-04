# How to Run (v0)

## 1) Update staging files
Edit the CSVs in `data/templates/`:
- `workers.csv`
- `availability.csv`
- `work_orders.csv`
- `ot_totals.csv` (optional)

## 2) Run allocation
```bash
python3 scripts/otrak_v0.py
```

## 3) Review output
The draft plan is written to:
```
data/outputs/draft_assignments.csv
```

## Notes
- One-shift-per-worker rule is enforced in v0.
- Qualifications are hard filters; trade is not.
- Overrides are manual in the output CSV.
