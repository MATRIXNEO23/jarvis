/**
 * Jarvis <-> official @siwc/local adapter.
 *
 * A single private child process communicates over stdin/stdout JSON lines.
 * No local HTTP admin server, no API keys, no paid API fallback.
 * The OAuth redirect server is created and managed by the official SDK only
 * during sign-in. Credentials use Windows DPAPI (current user).
 */
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { createInterface } from "node:readline";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const appData = process.env.LOCALAPPDATA || join(process.env.USERPROFILE || ".", "AppData", "Local");
const sdkEntry = resolve(appData, "Jarvis", "runtime", "siwc", "packages", "local", "dist", "index.js");
const credentialDir = resolve(appData, "Jarvis", "gpt_account");

function emit(record) {
  process.stdout.write(JSON.stringify(record) + "\n");
}
function safeError(error) {
  const msg = error instanceof Error ? error.message : "Errore sconosciuto";
  return String(msg).slice(0, 500).replace(/Bearer\s+\S+/gi, "Bearer [omesso]");
}
function validateBrowserUrl(value) {
  const url = new URL(value);
  if (url.origin !== "https://auth.openai.com") {
    throw new Error("Indirizzo OAuth inatteso, apertura bloccata.");
  }
  return url.toString();
}

// Avoid passing secrets in process command-line arguments.
// PowerShell reads base64 from stdin and uses .NET DPAPI (CurrentUser).
// Encryption occurs only when SDK persists or loads credentials, not per token.
const POWERSHELL_DPAPI = `
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Security
$raw = [Convert]::FromBase64String([Console]::In.ReadToEnd().Trim())
if ($env:JARVIS_DPAPI_MODE -eq 'encrypt') {
  $result = [Security.Cryptography.ProtectedData]::Protect(
    $raw, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
} elseif ($env:JARVIS_DPAPI_MODE -eq 'decrypt') {
  $result = [Security.Cryptography.ProtectedData]::Unprotect(
    $raw, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
} else { throw 'Invalid DPAPI operation' }
[Console]::Out.Write([Convert]::ToBase64String($result))
`;
const encodedPowerShell = Buffer.from(POWERSHELL_DPAPI, "utf16le").toString("base64");

function dpapi(mode, buffer) {
  if (process.platform !== "win32") {
    return Promise.reject(new Error("Questo bridge richiede Windows DPAPI."));
  }
  return new Promise((resolveResult, reject) => {
    const child = spawn(
      "powershell.exe",
      ["-NoProfile", "-NonInteractive", "-EncodedCommand", encodedPowerShell],
      { windowsHide: true, stdio: ["pipe", "pipe", "pipe"],
        env: { ...process.env, JARVIS_DPAPI_MODE: mode } }
    );
    const timeout = setTimeout(() => child.kill(), 20_000);
    let output = "";
    child.stdout.setEncoding("utf8");
    child.stdout.on("data", chunk => {
      output += chunk;
      if (output.length > 1_000_000) child.kill();
    });
    // Stderr may contain sensitive context. Never forward to UI or logs.
    child.stderr.resume();
    child.on("error", err => { clearTimeout(timeout); reject(err); });
    child.on("close", code => {
      clearTimeout(timeout);
      if (code !== 0) {
        reject(new Error("Windows DPAPI non disponibile o credenziali non decifrabili."));
        return;
      }
      try {
        resolveResult(Buffer.from(output.trim(), "base64"));
      } catch {
        reject(new Error("Risposta DPAPI non valida."));
      }
    });
    child.stdin.on("error", () => {});
    child.stdin.end(Buffer.from(buffer).toString("base64"), "utf8");
  });
}

const encryption = {
  id: "jarvis-windows-dpapi-user-v1",
  isAvailable: () => process.platform === "win32",
  async encrypt(value) {
    return new Uint8Array(await dpapi("encrypt", Buffer.from(value, "utf8")));
  },
  async decrypt(value) {
    return (await dpapi("decrypt", Buffer.from(value))).toString("utf8");
  },
};

let sdk = null;
async function initialize() {
  if (process.platform !== "win32") throw new Error("Jarvis GPT supporta per ora Windows.");
  if (!existsSync(sdkEntry)) {
    throw new Error("SDK Sign in with ChatGPT non installato. Esegui installa_gpt.ps1.");
  }
  const { createChatGPT } = await import(pathToFileURL(sdkEntry).href);
  sdk = createChatGPT({
    appName: "Jarvis",
    appId: "jarvis-local",
    redirectPort: 0,
    storageDir: credentialDir,
    credentialEncryption: encryption,
    openBrowser: async (value) => emit({
      event: "open_browser", url: validateBrowserUrl(value),
    }),
  });
  return sdk.getSession();
}

async function execute(req) {
  const action = req.action;
  if (action === "status") return sdk.getSession();
  if (action === "sign_in") return sdk.signIn();
  if (action === "cancel_sign_in") {
    sdk.cancelSignIn();
    return { cancelled: true };
  }
  if (action === "disconnect") {
    await sdk.disconnect();
    return { status: "disconnected" };
  }
  if (action === "models") {
    const models = await sdk.listModels();
    return { models: models.map(model => ({ slug: model.slug, name: model.name || model.slug })) };
  }
  if (action === "ask") {
    const prompt = req.prompt;
    if (typeof prompt !== "string" || !prompt.trim() || prompt.length > 5000) {
      throw new Error("Messaggio GPT vuoto o troppo lungo (massimo 5000 caratteri).");
    }
    const state = await sdk.getSession();
    if (state.status !== "connected" || !state.sharing) {
      throw new Error("ChatGPT non connesso o permesso di utilizzo del piano non concesso.");
    }
    const models = await sdk.listModels();
    if (!models.length) throw new Error("Nessun modello disponibile per questo account.");
    const requested = typeof req.model === "string" ? req.model : "";
    const model = models.find(m => m.slug === requested) || models[0];
    const response = await sdk.streamResponse({ model: model.slug, input: prompt });
    if (!response.text || !response.text.trim()) throw new Error("GPT non ha fornito una risposta completa.");
    return { text: response.text.slice(0, 30000), model: model.slug };
  }
  throw new Error("Azione GPT non consentita.");
}

const awaiting = new Set();

try {
  const session = await initialize();
  emit({ event: "ready", session });
  // IMPORTANT: install readline only after asynchronous SDK initialization.
  // If created earlier, piped stdin can close while OAuth storage is loading;
  // its lines are discarded before for-await begins and Node exits with code 13
  // for an unsettled top-level await. This also affects Windows smoke tests.
  const input = createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of input) {
    let req;
    try {
      req = JSON.parse(line);
      if (!Number.isSafeInteger(req.id) || req.id < 1) {
        throw new Error("Identificativo richiesta non valido.");
      }
      if (req.action === "shutdown") {
        sdk.cancelSignIn();
        emit({ id: req.id, ok: true, result: { stopped: true } });
        break;
      }
      const operation = execute(req)
        .then(result => emit({ id: req.id, ok: true, result }))
        .catch(error => emit({ id: req.id, ok: false, error: safeError(error) }));
      awaiting.add(operation);
      void operation.finally(() => awaiting.delete(operation));
    } catch (error) {
      emit({ id: req?.id || 0, ok: false, error: safeError(error) });
    }
  }
  // When piped input reaches EOF, finish all accepted requests before exit.
  // Otherwise a successful 'ready' event may conceal a missing response.
  await Promise.allSettled([...awaiting]);
} catch (error) {
  emit({ event: "fatal", error: safeError(error) });
  process.exitCode = 1;
}
