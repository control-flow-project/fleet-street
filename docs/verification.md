# Verification — 2026-10-17

## Scope

This record covers the public example's configuration, local tools, instructions
and report output. It does not certify a live Matrix deployment, paid model
responses, actual venue facts or the quality of a future analytical answer.
No real fleet is enrolled or activated, and no public report is published through
crossfire. Existing controllers, user credentials and native histories are not
used or changed.

## Environment and commands

Linux amd64; Python 3.14.4; Node 26.8.1; public `@ctlflow/fleet` and
`@ctlflow/fleetd` 0.1.20; Playwright 1.63.0; Chrome 155.0.8059.84. The host has
Codex CLI 0.163.0, but verification performs zero native model turns.

All test processes, including the temporary controller and browser, run inside
an 8 GiB, zero-swap, 256-task aggregate scope. No GitHub CI/CD is configured.
The npm seven-day external release-age policy is retained. The only named
exclusions are the same two owned public fleet packages already excluded in
ctlflow; no external dependency is exempted.

```sh
npm ci --ignore-scripts --cache .temp/npm
npm run check
```

Run these commands under the resource scope shown in the README.

## Results

| Check | Result |
| --- | --- |
| Python tests | 32 cases, including exact arithmetic, rounding, invalid input, private setup, output preservation, HTML escaping and hand-off arguments |
| Official installed fleet loader | Ten Codex instances accepted through an isolated controller |
| Invalid duplicate registered name within roster | Rejected by official loader |
| Unimplemented runtime and unsupported effort | Rejected by official loader |
| Per-instance effort override | Accepted and retained in the inspected roster |
| Stopped readiness check | Fails without starting an agent |
| Native model turns or enrollment | Zero |
| Report browser tests | Two cases; local assets, exact figures, opaque-origin storage denial and no console errors |
| Report widths | 320, 390, 768 and 1440 px without page-level overflow |
| Shared skills | Five pass the Codex skill validator |
| Instructions | Ten distinct role procedures and one shared routing directory; reviewed for scope and disclosure rules |
| Static report | Exactly four files; no remote resources, scripts, source-directory copying or automatic publication |
| Licenses/package metadata | MIT; package private; no external source material included |

The first acceptance run rejected copied negative fixtures because the test's
copy operation left their root group-writable. The fixture owner now explicitly
sets private directory/file modes before testing the intended schema failures;
the product's ownership checks are unchanged. Browser verification then found an
automatic favicon request outside the report bundle. The report now names its
local authored SVG as its favicon; the no-missing-assets assertion is retained.

The browser sandbox check verifies this report under a sandboxed local HTTP
response. It is not a new certification of crossfire's production cookie, TLS or
reverse-proxy configuration. Actual cross-server name collisions and live room
authorization remain platform behavior, not simulated success here.

Inactive test controller state, browser fixtures, dependency installations and
caches are removed after use. Preserve operating `.local/fleet/` state in real
deployments; it is not a test artifact.
