import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { isAbsolute } from 'node:path';
const [distribution] = process.argv.slice(2);
assert(process.argv.length === 3 && distribution && isAbsolute(distribution), 'Supply an absolute native ctlflow distribution directory');
for (const args of [['test'], ['run', 'test:fleet', '--', distribution], ['run', 'test:browser']]) {
  const result = spawnSync('npm', args, { stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}
