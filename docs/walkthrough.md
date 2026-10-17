# A fictional studio feasibility brief

This example demonstrates collaboration, not current London theatre research.
The venue, company, rates and expected attendance are invented. There is no
actual production, availability, rights clearance or booking.

## Human request

After setup, grant the stage manager access to a project room and configure the
intended human wake senders. Ask:

> Use the fictional River Bell brief and cost inputs from the example repository.
> Can the three performances cover those costs? Give me the useful numbers and
> the important questions before committing. Coordinate the necessary review.
> Do not contact anyone, book anything, spend money or publish a public report.

The [brief](../examples/brief.json) supplies the starting assumptions. A real
mention can interrupt the stage manager; an ordinary message from an eligible
sender follows the instance's normal delivery policy.

## Assignment and specialist access

The stage manager selects the budget analyst and fact-checker for the arithmetic.
It may ask production, venue, access or rights specialists to identify material
uncertainties, without giving every role a parallel research assignment.

Use the installed client from the fleetd-provided project/profile:

```sh
PROJECT="$CROSSFIRE_PROJECT"
PROFILE="$CROSSFIRE_AGENT_NAME"
CLIENT="$PROJECT/.crossfire/client.mjs"
node "$CLIENT" --project "$PROJECT" --profile "$PROFILE" agent directory
node "$CLIENT" room invite-agent --help
```

The directory returns both internal agent identifiers and actual Matrix IDs.
Room access tools take the agent identifier; mention metadata takes the Matrix
user ID. Neither is a displayed name. The stage manager's invitation still needs
its current per-room and native authority. Do not guess identifiers or substitute
a direct Matrix invite if crossfire denies access.

The [hand-off text](../examples/handoff.md) identifies the question, permitted
inputs and stopping point. Replace the sample origin note with the real delivered
room/event attribution, and save the actual message as a private Markdown file.
To deliberately interrupt and assign a specialist:

```sh
sh examples/send-handoff.sh "$ROOM_ID" "$RECIPIENT_MATRIX_ID" \
  "$TRANSACTION_ID" "$HANDOFF_MARKDOWN_FILE"
```

The wrapper passes `--mention-user` to the native client. Its transaction ID is
explicit and stable for an identical uncertain retry. Room membership and wake
rules remain separate checks. Do not mention agents for every acknowledgement.

## Reproducible calculation

From the repository root:

```sh
python3 -m tools.fleet_street budget --input examples/budget.json \
  --output .local/budget.json
```

For an operating agent, pass an absolute output path under its own ignored
workarea instead. The tool validates structured inputs and computes:

| Item | Fictional result |
| --- | ---: |
| Available paid tickets | 360 |
| Expected paid tickets at the supplied occupancy | 270 |
| Gross ticket receipts | GBP 4,995.00 |
| Ticket fees | GBP 249.75 |
| Net receipts | GBP 4,745.25 |
| Base costs | GBP 4,730.00 |
| Contingency | GBP 473.00 |
| Total costs | GBP 5,203.00 |
| Balance | GBP -457.75 |
| Paid break-even | 297 tickets, 82.50% of saleable capacity |

The calculation excludes tax/VAT, payroll and cash-flow timing, grants, mixed
ticket prices and variable royalties. Consult the
[calculation basis](../fleet/.agents/skills/production-budget/references/calculation.md).
The tools do not decide whether the inputs are realistic.

## Review and reply

The fact-checker reproduces the material numbers and tests whether the conclusion
matches the question. Venue availability, commercial inclusions, rights and access
remain unknown, not confirmed merely because arithmetic passed. Findings should
preserve material disagreement and identify who needs to confirm each point.

The stage manager answers the human in the originating room through the messaging
tool. It reports the gap, basis and unresolved decisions. A terminal statement
does not reach that room automatically; terminal output goes to the owner's DM.
Local paths are not download links. Use an authorized attachment or an approved
public report if the human needs an artifact they can access.

## Optional public report

The original request explicitly forbids publication. The human must separately
authorize public disclosure of the intended report before the native publication
command is run. Creating the local draft below does not publish it:

```sh
python3 -m tools.fleet_street report --input examples/report.json \
  --budget examples/budget.json --directory .local/public-report
```

Review all five files: `index.html`, `assets/report.css`,
`assets/proscenium.svg`, `assets/LICENSE.txt` and `data/budget.json`. The report formats supplied claims;
it is not an automatic fact-check or private-information detector.

After explicit release permission, an enrolled agent can run:

```sh
node "$CLIENT" --project "$PROJECT" --profile "$PROFILE" report publish \
  --directory .local/public-report --title 'The River Bell — fictional example'
```

Use the actual draft path. The publisher returns the real URL; do not construct
one from a guessed content domain. Send that URL to the intended room and explain
that anyone with the link can read every published file. The isolated report
origin does not make the content confidential. The owner can delete the report
through management but cannot recall downloaded copies.
