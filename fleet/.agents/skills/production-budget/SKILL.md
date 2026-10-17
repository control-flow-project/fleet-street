---
name: production-budget
description: Calculate and review paid-ticket theatre scenarios from explicit structured assumptions using the local Decimal budget tool.
---

For the simple paid-ticket scenario, use `budget`, not mental arithmetic. From
the repository root:

```sh
python3 -m tools.fleet_street budget --input examples/budget.json \
  --output .local/budget.json
```

For real work use the actual authorized input and an output in your own ignored
workarea. The command refuses to replace an existing output. Use a new filename
for a revised scenario so an earlier result is not silently overwritten.

Read [the calculation basis](references/calculation.md) before interpreting
totals. It defines receipts, costs, contingency and break-even, and states what
the tool does not model. The fictional fixture is not a rate card or demand
forecast. Rerun the tool when inputs change; do not patch formatted totals.

Confirm seat definitions, rates, inclusions, units and fee/tax treatment with the
relevant specialists. Compare coherent scenarios and describe uncertainty. These
methods are non-exclusive; use a separate explicit model for arrangements outside
the tool's supported basis, with its assumptions and calculations available for
independent review.
