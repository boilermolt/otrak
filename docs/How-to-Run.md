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

## 4) Search agreements (keyword)
```bash
python3 scripts/search_agreements.py --list
python3 scripts/search_agreements.py --q "overtime" --limit 5
python3 scripts/search_agreements.py --q "overtime" --trade "IBEW"
python3 scripts/search_agreements.py --q "overtime premium" --agreement "Nuclear Project" --phrase
python3 scripts/search_agreements.py --q "overtime\s+premium" --regex
```

## 5) Semantic search (embeddings)
```bash
/media/boilerrat/Bobby/otrak-venv/bin/python scripts/search_embeddings.py --q "overtime premium" --limit 5
/media/boilerrat/Bobby/otrak-venv/bin/python scripts/search_embeddings.py --q "rest period" --trade "IBEW"
```

## 6) Extract overtime facts from agreements (proposed queue)
```bash
python3 scripts/extract_overtime_facts.py
# output: data/contract_facts/overtime_facts.jsonl
```

## 7) Review + approve facts
- Open `data/contract_facts/overtime_facts.jsonl`
- Change `"status": "proposed"` to `"approved"` for facts you want to compile.

## 8) Compile approved facts into generated rules
```bash
python3 scripts/compile_contract_rules.py
# output: data/contract_facts/rules.generated.json
```

## 9) Simple Flask UI
```bash
/media/boilerrat/Bobby/otrak-venv/bin/python app/app.py
# visit http://localhost:5000
```

## 10) Docker
```bash
docker compose up --build
# visit http://localhost:5000
```

## Notes
- One-shift-per-worker rule is enforced in v0.
- Qualifications are hard filters; trade is not.
- Overrides are manual in the output CSV.
- Contract fact extraction is heuristic and must be human-reviewed before use.
