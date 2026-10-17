# Paid-ticket calculation basis

The input uses GBP decimal strings for money and rates. Quantities are positive
integers. `occupancy` is the expected fraction of saleable paid seats, from zero
to one. `fee_rate` is a proportion of gross receipts, below one. Cost quantities
and rates are independent of ticket sales.

- Available tickets = performances × saleable seats per performance.
- Expected paid tickets = available tickets × occupancy; this is an expectation,
  not a guarantee or a physical fractional ticket sold.
- Gross receipts = expected paid tickets × ticket price.
- Ticket fees = gross receipts × fee rate.
- Net receipts = gross receipts − ticket fees.
- Base costs = sum of quantity × unit cost for each cost line.
- Contingency = base costs × contingency rate.
- Total costs = base costs + contingency.
- Balance = net receipts − total costs.
- Break-even paid tickets = total costs divided by net receipts per ticket,
  rounded upward, then checked against capacity using the same currency rounding.

Money is rounded to pence using ROUND_HALF_UP at the displayed line/receipt
boundaries. Break-even must actually cover total costs under those boundaries;
the tool verifies the first candidate and its preceding ticket count.

The example excludes VAT/tax, payroll deductions, timing of cash flows,
refundable deposits, grants, variable royalties, mixed ticket prices and finance.
Do not imply that these are absent from a real production. Keep such costs or
funding arrangements explicit in another appropriate calculation.

The fixture produces net receipts of GBP 4,745.25 and total costs of GBP
5,203.00: a GBP 457.75 gap. It requires 297 paid tickets to break even on the
stated basis. These are arithmetic results for invented assumptions.
