---
name: review-handoff
description: Assign a theatre specialist or request independent review while preserving the source room, evidence and intended stopping point.
---

Give the recipient the assignment ID, exact originating room/event, question,
authorized inputs, assumptions, useful deliverable and what not to do. The
sample `examples/handoff.md` is a budget review, not a universal template.

Resolve current identities with the installed `agent directory`. Use managed
room invitation/access tools if the recipient needs admission; do not bypass
crossfire with a native Matrix invite. Hand off in the original room when
possible. Do not transfer another room's private information without permission.

The repository's `examples/send-handoff.sh` invokes the installed client with a
stable transaction ID and an explicit `--mention-user`. It does not guess a
recipient, create a room or grant wake permission. A real mention interrupts;
routine updates should be ordinary room messages. Keep the transaction ID and
content identical for an uncertain retry. Changed content requires a new ID.

An independent review should report evidence-backed corrections and unknowns,
not endorse a predetermined answer. Return material disagreements to the stage
manager. Close completed work without acknowledgement loops. New substantive
questions can warrant a new review; rechecking unchanged output does not.
