# fleet-street

This is a public, MIT-licensed example fleet for London theatre work. The
repository owns ten Codex role definitions, shared instructions, fictional
examples and local command-line tools. crossfire owns identity, permissions and
messaging; fleetd owns agent processes, histories, delivery and recovery. Do not
reimplement those responsibilities here.

Keep one current configuration format and command path. Do not add compatibility
aliases, alternate listeners, services, database infrastructure or automatic
downloads. Tools use the Python standard library; the exact public fleet release
is a development dependency for integration verification, not a runtime fork.

Keep all ten role definitions, the roster and the routing directory aligned.
Give each role its own workarea. Shared instructions and skill references live
once beneath `fleet/`; role instructions define responsibilities, questions,
deliverables and limits. A stage manager coordinates rather than impersonating
the specialists. Examples are non-exclusive, not an exhaustive analytical method.

No private fleet names, prompts, source documents, credentials, endpoints, machine
details or operating data belong in this public repository. Fixtures are clearly
fictional. Generated working fleets, outputs, credentials and native histories
belong only in ignored private directories. Do not activate a real fleet, contact
venues, buy tickets, publish a report or change external permissions as a test.

Use functional typed modules, validation at file/CLI boundaries and explicit
errors. Keep code examples executable and documentation factual. Never use
promotional claims or imply that an agent's output replaces professional advice,
venue confirmation or an access user's stated needs.

Run build/test commands in a finite aggregate process group. On Linux use an
8 GiB MemoryMax, zero MemorySwapMax and TasksMax 256 systemd user scope. Remove
regenerated fixtures, dependencies and caches after their final use; preserve
authored examples, private operating state and concise verification evidence.
Record necessity and verification in `.analysis/necessity-ledger.md`.

Never commit/push main, force-push, discard shared work or create a PR. The owner
creates PRs manually from the prepared branch. Git identity is
jeswin <jeswinpk@agilehead.com>. No new delegated work without explicit approval.
