import assert from "node:assert/strict";
import { once } from "node:events";
import fs from "node:fs";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { setTimeout as delay } from "node:timers/promises";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const temporary = path.join(root, ".temp");
fs.mkdirSync(temporary, { recursive: true });
const fixture = fs.mkdtempSync(path.join(temporary, "fleet-"));
const controllerRoot = path.join(fixture, "controller");
const fleetRoot = path.join(fixture, "working");
const cli = fileURLToPath(import.meta.resolve("@ctlflow/fleet/executable"));
const daemonEntry = fileURLToPath(import.meta.resolve("@ctlflow/fleetd/executable"));
const version = JSON.parse(fs.readFileSync(fileURLToPath(import.meta.resolve("@ctlflow/fleet/package.json")), "utf8")).version;
assert.equal(version, "0.1.20");
const environment = { ...process.env, HOME: path.join(fixture, "home"), CODEX_HOME: path.join(fixture, "native-home"),
  XDG_CONFIG_HOME: path.join(fixture, "config"), XDG_STATE_HOME: path.join(fixture, "state"), XDG_DATA_HOME: path.join(fixture, "data") };
for (const directory of [environment.HOME, environment.CODEX_HOME, environment.XDG_CONFIG_HOME, environment.XDG_STATE_HOME, environment.XDG_DATA_HOME]) fs.mkdirSync(directory, { mode: 0o700 });
let daemon;
let ended;
let diagnostics = "";

function call(arguments_, expectedSuccess = true) {
  const result = spawnSync(process.execPath, [cli, "--root", controllerRoot, ...arguments_], { cwd: root, env: environment, encoding: "utf8", timeout: 15000, maxBuffer: 2 * 1024 * 1024 });
  assert.equal(result.error, undefined, result.error?.message);
  if (expectedSuccess) {
    assert.equal(result.status, 0, result.stderr.slice(0, 4000));
    return JSON.parse(result.stdout);
  }
  assert.notEqual(result.status, 0, "Invalid configuration must fail");
  return result.stderr;
}

function copyFixture(directory) {
  fs.cpSync(fleetRoot, directory, { recursive: true });
  function permissions(current) {
    fs.chmodSync(current, 0o700);
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const filename = path.join(current, entry.name);
      if (entry.isDirectory()) permissions(filename);
      else fs.chmodSync(filename, 0o600);
    }
  }
  permissions(directory);
}

try {
  const configuration = spawnSync("python3", ["-c", "from pathlib import Path; from tools.fleet_street.configuration import configure; import sys; configure('https://example.test', '@owner:example.test', 'check', destination=Path(sys.argv[1]))", fleetRoot], { cwd: root, env: environment, encoding: "utf8", timeout: 10000 });
  assert.equal(configuration.status, 0, configuration.stderr);
  daemon = spawn(process.execPath, [daemonEntry, "--root", controllerRoot, "--name", "fleet-street-check"], { cwd: root, env: environment, stdio: ["ignore", "pipe", "pipe"] });
  ended = once(daemon, "exit");
  daemon.stdout.on("data", chunk => { diagnostics = (diagnostics + chunk).slice(-4000); });
  daemon.stderr.on("data", chunk => { diagnostics = (diagnostics + chunk).slice(-4000); });
  const deadline = Date.now() + 15000;
  while (!fs.existsSync(path.join(controllerRoot, "fleetd.sock"))) {
    assert.equal(daemon.exitCode, null, diagnostics);
    assert.equal(Date.now() < deadline, true, "Isolated controller readiness deadline");
    await delay(25);
  }
  call(["daemon", "status"]);
  const added = call(["add", fleetRoot]);
  assert.equal(added.instances.length, 10);
  const shown = call(["show", "fleet-street"]);
  assert.equal(shown.instances.every(instance => instance.desiredActive === false && instance.listenerActive === false && instance.sessionId === null), true, "No enrollment or agent execution");
  assert.equal(shown.instances.every(instance => instance.instance.name === "check-" + instance.instance.key), true);
  assert.equal(call(["agent", "list", "fleet-street"]).length, 10);
  assert.match(call(["test", "fleet-street"], false), /stopped|not ready/iu);
  for (const [label, alter, expected] of [
    ["duplicate-name", directory => { const filename = path.join(directory, "runtime.toml"); fs.writeFileSync(filename, fs.readFileSync(filename, "utf8").replace('name = "check-dramaturg"', 'name = "check-stage-manager"')); }, /Duplicate instance name/u],
    ["unsupported-runtime", directory => { const filename = path.join(directory, "agents/dramaturg/agent.toml"); fs.writeFileSync(filename, fs.readFileSync(filename, "utf8").replace('runtime = "codex"', 'runtime = "claude"')); }, /codex|runtime|pi|Expected/iu],
    ["unsupported-effort", directory => { const filename = path.join(directory, "agents/dramaturg/agent.toml"); fs.writeFileSync(filename, fs.readFileSync(filename, "utf8").replace('model_reasoning_effort = "high"', 'model_reasoning_effort = "imaginary"')); }, /effort|Expected|supported/iu],
  ]) {
    const invalid = path.join(fixture, label);
    copyFixture(invalid);
    alter(invalid);
    assert.match(call(["add", invalid], false), expected, label);
  }
  const override = path.join(fixture, "override");
  copyFixture(override);
  const rosterPath = path.join(override, "runtime.toml");
  fs.writeFileSync(rosterPath, fs.readFileSync(rosterPath, "utf8").replace('fleet = "fleet-street"', 'fleet = "override-example"').replace('[instances.listener_options]', '[instances.runtime_options]\nmodel_reasoning_effort = "high"\n\n[instances.listener_options]'));
  const overridden = call(["add", override]);
  assert.equal(overridden.instances[0].instance.runtimeOptions.model_reasoning_effort, "high");
  const local = path.join(fixture, "loopback");
  copyFixture(local);
  const localRoster = path.join(local, "runtime.toml");
  fs.writeFileSync(localRoster, fs.readFileSync(localRoster, "utf8").replace('fleet = "fleet-street"', 'fleet = "loopback-example"').replace('server = "https://example.test"', 'server = "http://127.0.0.1:8080"'));
  assert.equal(call(["add", local]).instances.length, 10, "Native loopback development origin accepted");
  assert.equal(call(["show", "fleet-street"]).instances.every(instance => !instance.desiredActive), true);
  console.log(JSON.stringify({ release: version, agents: 10, officialLoader: "passed", rejected: ["duplicate name", "unimplemented runtime", "unsupported effort"], perInstanceOverride: "passed", loopbackOrigin: "passed", stoppedReadiness: "rejected", modelTurns: 0, enrollment: false }));
} finally {
  try {
    if (daemon && daemon.exitCode === null) {
      daemon.kill("SIGTERM");
      let timer;
      try {
        await Promise.race([ended, new Promise((resolve, reject) => { timer = setTimeout(() => { daemon.kill("SIGKILL"); reject(new Error("Owned test controller did not stop")); }, 5000); })]);
      } finally { clearTimeout(timer); }
    }
  } finally { fs.rmSync(fixture, { recursive: true, force: true }); }
}
