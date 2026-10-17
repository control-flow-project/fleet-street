# fleet-street

A ten-agent London theatre example for ctlflow. People talk to the agents in
Matrix rooms; crossfire manages identities and access, and fleetd runs the Codex
sessions on the owner's machine. This repository supplies roles, shared skills,
fictional inputs and offline tools, not another server or listener.

The sample is MIT licensed. It does not represent a theatre company, a real
production or current venue prices. No booking, external contact, expenditure
or report publication happens during configuration or tests.

## Roles

Start with the stage manager for a mixed brief. Contact a specialist directly
for a question in its area. The stage manager normally invites only the roles
the task needs, rather than putting all ten into every room.

| Local key | Work | Instructions |
| --- | --- | --- |
| stage-manager | Scope, routing, dependencies and synthesis | [Role](fleet/agents/stage-manager/AGENTS.md) |
| dramaturg | Dramatic structure and audience experience | [Role](fleet/agents/dramaturg/AGENTS.md) |
| venue-scout | Venue fit and facts requiring confirmation | [Role](fleet/agents/venue-scout/AGENTS.md) |
| production-planner | People, schedule and technical dependencies | [Role](fleet/agents/production-planner/AGENTS.md) |
| budget-analyst | Explicit cost scenarios and funding gaps | [Role](fleet/agents/budget-analyst/AGENTS.md) |
| accessibility-reviewer | Access information, barriers and provisions | [Role](fleet/agents/accessibility-reviewer/AGENTS.md) |
| audience-researcher | Audience hypotheses and evidence | [Role](fleet/agents/audience-researcher/AGENTS.md) |
| publicity-editor | Listings, practical copy and report drafts | [Role](fleet/agents/publicity-editor/AGENTS.md) |
| rights-researcher | Material inventory and permissions questions | [Role](fleet/agents/rights-researcher/AGENTS.md) |
| fact-checker | Independent claim and calculation review | [Role](fleet/agents/fact-checker/AGENTS.md) |

See [the routing directory](fleet/directory.md) and
[shared working instructions](fleet/AGENTS.md). The stage manager runs at medium
effort; the other nine at high. All use Codex. No exact model is assumed to exist
on every account: omit `--model` to use Codex's configured default, or supply an
exact available ID. fleetd rejects unsupported model/effort combinations; it does
not substitute a different model or effort.

## Requirements

- A crossfire account and a server matching the pinned public release, **0.1.20**.
- Node 26+, npm 11.17+ and Python 3.11+ on the agent machine.
- A working Codex installation and the owner's provider login on that machine.
- An Element client for the same Matrix account.

The example is tested with Codex CLI 0.163.0 installed, but its offline acceptance
does not run model turns. Browsing/search capabilities depend on the operator's
native session; this repository does not install a browser skill or provider.
Toolsmith is optional and is not required by these tools.

Native options explicitly select `danger-full-access` and `on-request`, matching
the platform's defaults. This is not an OS sandbox: agents can access files
available to the host account. Review these options before starting real work.
Private file modes and instructions are not isolation between same-user agents.

## Prepare a working fleet

Clone the repository, change into it and use your actual public server origin,
human Matrix ID and a short unique agent-name prefix.

An HTTPS origin is used for a remote instance. Native loopback HTTP origins are
also accepted for local development; HTTP to other hosts is rejected.

For example:

```sh
git clone https://github.com/control-flow-project/fleet-street.git
cd fleet-street
python3 -m tools.fleet_street configure \
  --server https://chat.example.org \
  --owner '@alice:chat.example.org' --prefix alice-fs
```

This creates `.local/fleet/runtime.toml` and the ten role definitions, routing
guide and skills. It fills every owner wake rule and uses names such as
`alice-fs-stage-manager`. The operator chooses the prefix; registered names must
be unique across the server. A collision is an error, not an automatic suffix.

For an explicit model selection, add `--model EXACT_AVAILABLE_MODEL_ID` to this
command. Without it the model field is omitted. The generator does not query the
provider, enroll identities or start a controller. Review the generated files.

An identical repeated configure command preserves existing instructions, native
histories and state. Different origin, owner, names or model selection is rejected
without replacing the working fleet. Use the saved configuration for subsequent
setup and lifecycle actions; do not delete `.local/` to repair a problem.

## Connect to crossfire

Install the exact public fleet tools locally, without lifecycle install scripts:

```sh
npm ci --ignore-scripts --cache .temp/npm
./node_modules/.bin/fleet setup --config "$(pwd)/.local/fleet/runtime.toml"
./node_modules/.bin/fleet agent list fleet-street
./node_modules/.bin/fleet test fleet-street
```

Use the personalized setup instructions from your instance and its matching
release. They remain authoritative if the instance has moved beyond this sample's
pin. Setup asks the human to approve the exact roster through crossfire; this
repository cannot approve itself. It starts separate managed histories and does
not attach the agent or terminal session that performed installation.

The default wake policy allows the selected owner and that owner's active agents,
including agents outside this example fleet. Room access, delivery and mute rules
still apply. Other people do not wake the agents until the owner configures them
in management. Enrollment does not create room membership or eager owner DMs.

In Element create a room for the project. Through crossfire grant the stage
manager reply access. Its reviewed invitation capability lets it bring in needed
registered specialists, subject to its actual room authority. The other roles
have no invitation capability by default. A temporary invitation is not a new
native process and does not move private information between rooms.

## Worked example

The [fictional brief](examples/brief.json) asks whether three studio performances
cover the supplied costs. The [walkthrough](docs/walkthrough.md) shows routing,
calculation, independent review and an optional report. Try the offline tools
before enrolling a fleet:

```sh
python3 -m tools.fleet_street budget --input examples/budget.json \
  --output .local/budget.json
python3 -m tools.fleet_street report --input examples/report.json \
  --budget examples/budget.json --directory .local/public-report
```

The supplied scenario produces GBP 4,745.25 net receipts, GBP 5,203.00 costs and
a GBP 457.75 gap. Its paid break-even is 297 tickets. These are calculations from
invented inputs, not a forecast, quote or recommendation.

The tools refuse to overwrite existing output. Use new output names for revised
scenarios. They accept small structured JSON inputs (maximum 1 MiB), validate
fields and use Decimal arithmetic. They do not interpret arbitrary HTML tables,
download data or maintain a database.

The local report contains HTML, CSS, an authored SVG, calculated budget JSON and
the MIT notice for the supplied assets.
Generating it is not publication. [Publication instructions](docs/walkthrough.md#optional-public-report)
explain explicit consent, the native client and who can see the resulting files.

## Files

```text
fleet/
  runtime.toml
  AGENTS.md
  directory.md
  .agents/skills/
  agents/<role>/{agent.toml,AGENTS.md}
examples/
  brief.json
  budget.json
  report.json
  handoff.md
  send-handoff.sh
tools/fleet_street/
  configuration.py
  budget.py
  report.py
  files.py
  validation.py
  cli.py
  assets/
docs/
  walkthrough.md
  operations.md
  verification.md
scripts/verify-fleet.mjs
tests/
.local/fleet/          generated, ignored working configuration and native state
.temp/                disposable test/install output
```

`fleet/` is the authored template. `.local/fleet/` is the only working fleet
created by the tool. Do not register the placeholder template as another fleet.
Never commit generated state, workareas, credentials or real research material.

## Verify and operate

Run the focused sample checks inside a bounded aggregate scope on Linux:

```sh
systemd-run --user --scope --quiet \
  --property=MemoryMax=8G --property=MemorySwapMax=0 --property=TasksMax=256 \
  --working-directory="$(pwd)" npm run check
```

`npm run check` runs Python tests, the installed public fleet/fleetd acceptance
and real-browser report checks. Integration creates an isolated, unenrolled
controller, registers fixture rosters, checks rejection paths and stops it. It
does not use the operator's saved controller, native login or Matrix account.
Browser checks use `BROWSER_EXECUTABLE` or `/usr/bin/google-chrome`; no browser is
downloaded. No GitHub CI/CD is configured.

- [Stop, resume, change instructions and diagnose failures](docs/operations.md)
- [Verification evidence and its limits](docs/verification.md)
- [ctlflow documentation](https://ctlflow.com/docs/)
