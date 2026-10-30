/**
 * Windows smoke test of the real local GPT bridge transport.
 * Does NOT authenticate, request models, or send any content to GPT.
 *
 * Starts the bridge as Jarvis does, waits for a ready event, then asks for
 * disconnected session state before shutting the child down.
 */
import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const bridge = join(root, "gpt_bridge.mjs");
const child = spawn(process.execPath, [bridge], {
  cwd: root,
  stdio: ["pipe", "pipe", "pipe"],
  windowsHide: true,
});
let buffer = "";
let state = "starting";
let finished = false;
let stderr = "";
const timer = setTimeout(() => abort("Timeout waiting for bridge"), 45_000);

function abort(reason) {
  if (finished) return;
  finished = true;
  clearTimeout(timer);
  process.stderr.write("GPT smoke test failed: " + reason + "\n");
  child.kill();
  process.exitCode = 1;
}

child.stdout.setEncoding("utf8");
child.stdout.on("data", (chunk) => {
  buffer += chunk;
  if (buffer.length > 65536) return abort("Oversized output");
  let index;
  while ((index = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, index).trim();
    buffer = buffer.slice(index + 1);
    if (!line) continue;
    let packet;
    try { packet = JSON.parse(line); }
    catch { return abort("Unexpected non-JSON stdout"); }
    if (packet.event === "fatal") return abort("SDK initialize failed");
    if (state === "starting" && packet.event === "ready") {
      if (packet.session?.status !== "disconnected") {
        return abort("Expected disconnected initial state");
      }
      state = "checking";
      child.stdin.write('{"id":1,"action":"status"}\n');
    } else if (state === "checking" && packet.id === 1) {
      if (packet.ok !== true || packet.result?.status !== "disconnected") {
        return abort("Status command did not report a disconnected session");
      }
      state = "stopping";
      child.stdin.write('{"id":2,"action":"shutdown"}\n');
    } else if (state === "stopping" && packet.id === 2) {
      if (packet.ok !== true) return abort("Shutdown rejected");
      state = "done";
      child.stdin.end();
    }
  }
});
child.stderr.setEncoding("utf8");
child.stderr.on("data", (chunk) => {
  // Don't expose arbitrary stderr contents (may contain private data).
  stderr = (stderr + chunk).slice(-1024);
});
child.on("error", () => abort("Unable to spawn Node child"));
child.on("exit", (code) => {
  if (finished) return;
  clearTimeout(timer);
  finished = true;
  if (state !== "done" || code !== 0) {
    process.stderr.write("GPT smoke test failed: bridge exited before status + shutdown; code=" + code + ", state=" + state + "\n");
    process.exitCode = 1;
  } else {
    process.stdout.write("GPT bridge initialized, replied disconnected, and shut down successfully (no login).\n");
  }
});
