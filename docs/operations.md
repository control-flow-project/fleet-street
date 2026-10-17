# Operating the example fleet

Use the exact fleet CLI installed for the instance. The commands here assume
its saved local controller profile and the generated fleet key `fleet-street`.
An explicit `--root` or configured SSH remote can select another controller;
do not reuse these examples against an unrelated operating fleet.

## Status

```sh
./node_modules/.bin/fleet show fleet-street
./node_modules/.bin/fleet agent list fleet-street
./node_modules/.bin/fleet test fleet-street
```

Readiness is not a completed task. A listener can be ready while a native session
sleeps; a saved history does not mean a process is running. Read the controller's
per-agent desired state, native phase, listener state and actual errors.

If a room receives no answer, check the actual registered identity, applied room
access, mute/delivery state and wake sender policy. A selected owner plus agents
rule includes that owner's agents, not every person or every fleet. Other humans
must be added explicitly in management if they should wake an agent. A successful
invitation alone does not establish successful input delivery or a finished task.

## Stop and resume

```sh
./node_modules/.bin/fleet stop fleet-street
./node_modules/.bin/fleet start fleet-street
./node_modules/.bin/fleet agent stop fleet-street budget-analyst
./node_modules/.bin/fleet agent start fleet-street budget-analyst
```

Normal start resumes the saved native histories, identity and configured options.
Stopping sessions prevents chat from waking them until resumed. Idle sleep is
different: fleetd keeps listening and an eligible message can wake the agent.
`deactivate`/`activate` controls delivery without replacing history.

Do not use `--fresh-history` to fix a delivery, login or configuration problem.
It is an explicit destructive context choice, not an ordinary resume. Preserve
the complete `.local/fleet/`, especially `.fleet/` and every workarea, through host
restarts. Re-cloning source does not reconstruct a lost native conversation.

## Change instructions and native settings

Stop the affected agent, or the whole fleet for shared instruction changes. Edit
the generated working files under `.local/fleet/`, inspect the change and start
the same saved agent again. Native options are checked by the runtime adapter;
unknown settings or unavailable model/effort combinations must fail explicitly.
Management-edited permissions and wake rules are not silently reset on resume.

`fleet/` is the source template for new working fleets. Configure does not recopy
new template instructions over an existing operating fleet. Deliberately review
and apply wanted instruction changes to the stopped working copy; preserve its
owner, names, native state and histories. Proposed roster/name/policy changes
require the normal stopped-fleet enrollment/owner review, not file deletion.

An instruction to reread AGENTS.md on resume helps apply edited guidance; it does
not create filesystem isolation. Shared history is the default. Per-room history
is an explicit per-instance option and still shares host tools and files.

## Native questions and failure

The verified owner answers native permission and structured-question requests
through the exact authenticated crossfire review links. A room mention or yes/no
text is not consent for a pending native permission. Do not auto-answer decisions.

For a failed agent, inspect its specific controller error and owner-DM notice.
Use `fleet agent contexts fleet-street INSTANCE` to inspect retained contexts.
For a running Codex session, `fleet agent attach fleet-street INSTANCE` prints the
native terminal attachment command. It does not wake a stopped/sleeping session
or start another listener. Do not expose that command or machine details to rooms.

## Update and storage

Use the instance's approved exact public release and its documented update flow.
Update the sample's dependency pin deliberately; never replace package versions
silently or bypass the npm release-age policy for external packages. The checked-in
named exclusions cover only the two owned public fleet packages, as in ctlflow.

Remove `.temp/` and development `node_modules/` after verification if no current
work needs them. Never include `.local/`, workareas, provider credentials or source
research material in a public commit or cleanup command. The sample provides no
automatic history cleanup or reset operation.
