---
name: public-report
description: Produce a local theatre report directory and release it through crossfire only when public disclosure is explicitly authorized.
---

Create a local draft from explicit report and budget inputs:

```sh
python3 -m tools.fleet_street report --input examples/report.json \
  --budget examples/budget.json --directory .local/public-report
```

This formats supplied statements and calculated figures; it does not verify
their truth, fetch sources or publish anything. For real work put the directory
in your ignored workarea. Its output includes only HTML, local CSS, an authored
SVG, the calculated budget JSON and the MIT asset notice. It does not copy your input directory.

Review all generated files, text, source links and names for the intended public
audience. Confirm explicit human authorization to release that information.
Room membership or a private request for a report is not public-release consent.
Use broader review when needed; these checks are not a guarantee against leaks.

Publish using the installed native client, not a new web server:

```sh
node "$CROSSFIRE_PROJECT/.crossfire/client.mjs" \
  --project "$CROSSFIRE_PROJECT" --profile "$CROSSFIRE_AGENT_NAME" \
  report publish --directory .local/public-report --title 'Theatre feasibility note'
```

Pass the actual draft directory; the example path above is repository-relative.
Wait for a successful returned `url`, then send that exact URL to the explicit
originating room. Explain that anyone with the link can view every published
file. A random path and an isolated browser sandbox are not confidentiality
controls. Owners can delete a publication through management, not recall copies.

The native publisher owns integrity checks and the public origin. Do not build
hash-checking loops, guess a content hostname or claim an uncertain commit
succeeded. Keep its publication ID and inspect that exact operation on uncertainty.
