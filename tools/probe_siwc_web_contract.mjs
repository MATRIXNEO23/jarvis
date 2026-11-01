/** Development-only Windows probe: actual pinned SDK, intercepted transport.
 * No login/session storage, live inference, web traffic or paid fallback.
 * The candidate lives briefly beside the SDK's compiled module in the runner.
 * Neither original SDK files nor Jarvis's runtime bridge are modified.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, unlink } from 'node:fs/promises';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

if (process.platform !== 'win32' || process.env.GITHUB_ACTIONS !== 'true' ||
    !process.argv.includes('--ci-only')) {
  throw new Error('This development probe requires an isolated Windows CI runner and --ci-only.');
}
const sdk = join(process.env.LOCALAPPDATA, 'Jarvis', 'runtime', 'siwc', 'packages', 'local');
const expected = {
  'types.ts': 'e80f3d2fd6c7bb976b2c83469c4453bf57b16e07',
  'responses.ts': 'dd9f6f6a5229e6b42f8e6328b5a2e48587d09bbf',
};
for (const [name, sha] of Object.entries(expected)) {
  const data = await readFile(join(sdk, 'src', name));
  const actual = createHash('sha1').update(`blob ${data.length}\0`).update(data).digest('hex');
  assert.equal(actual, sha, `Pinned upstream ${name} differs: review before adapting`);
}
const modulePath = join(sdk, 'dist', 'responses.js');
let candidate = await readFile(modulePath, 'utf8');
function replaceOnce(before, after) {
  assert.equal(candidate.split(before).length, 2, 'Compiled SDK anchor changed');
  candidate = candidate.replace(before, after);
}
// Experimental extension of the existing request/parser only. The actual
// upstream OAuth, encrypted store, timeout and error handling remain in use.
replaceOnce('store: false,', `store: false,
      ...(options.webSearch === true ? {
        tools: [{ type: 'web_search' }],
        include: ['web_search_call.action.sources'],
      } : {}),`);
replaceOnce('let completed = false;', 'let completed = false; let webEvidence = { searched: false, sources: [] };');
replaceOnce('completed = true;', `if (options.webSearch === true) webEvidence = probeWebEvidence(event.response);
        completed = true;`);
replaceOnce('return { text };', 'return { text, ...webEvidence };');
candidate += `
function probeWebEvidence(response) {
  let searched = false;
  const found = new Map();
  const add = source => {
    if (!source || typeof source.url !== 'string' || source.url.length > 2048 || found.size >= 8) return;
    try {
      const url = new URL(source.url);
      if (url.protocol !== 'https:' || url.username || url.password) return;
      found.set(url.href, { url: url.href, title: typeof source.title === 'string' ? source.title.slice(0, 160) : '' });
    } catch {}
  };
  for (const item of Array.isArray(response?.output) ? response.output : []) {
    if (item?.type === 'web_search_call' && item.status === 'completed') {
      searched = true;
      for (const source of Array.isArray(item.action?.sources) ? item.action.sources : []) add(source);
    }
    if (item?.type === 'message') for (const part of Array.isArray(item.content) ? item.content : []) {
      for (const annotation of Array.isArray(part?.annotations) ? part.annotations : []) {
        if (annotation?.type === 'url_citation') add(annotation);
      }
    }
  }
  return { searched, sources: searched ? [...found.values()] : [] };
}
`;
const candidatePath = join(sdk, 'dist', 'jarvis-web-contract-probe.mjs');
const savedFetch = globalThis.fetch;
let requests = [];
let scenario = 'search';
const reply = '{"kind":"capability","action_id":"addon.accesso_file.localizza","arguments":{"query":"Fixture"}}';
const source = { type: 'url', url: 'https://example.com/fixture', title: 'Controlled fixture' };
function events() {
  const output = scenario === 'no_search' ? [] : [
    { type: 'web_search_call', status: 'completed', action: { type: 'search', sources: [source,
      ...(scenario === 'unsafe_sources' ? [
        { url: 'file:///C:/private' }, { url: 'javascript:alert(1)' },
        { url: 'https://user:pass@example.com/private' }, { url: 'invalid' },
      ] : [])] } },
    { type: 'message', content: [{ type: 'output_text', text: reply, annotations: [
      { type: 'url_citation', url: source.url, title: source.title, start_index: 0, end_index: 5 },
    ] }] },
  ];
  const data = [{ type: 'response.output_text.delta', delta: reply }];
  if (scenario === 'failed') data.push({ type: 'response.failed', response: { error: {
    code: 'tool_not_allowed', message: 'Controlled denial', type: 'invalid_request_error' } } });
  else if (scenario !== 'interrupted') data.push({ type: 'response.completed', response: { output } });
  return data.map(event => `event: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`).join('');
}
// Intercept every fetch before importing SDK modules. There is no network
// fallback: any unexpected destination fails the probe.
globalThis.fetch = async (input, init) => {
  const request = new Request(input, init);
  assert.equal(request.url, 'https://api.openai.com/v1/responses');
  requests.push(JSON.parse(await request.text()));
  return new Response(events(), { status: 200, headers: {
    'content-type': 'text/event-stream', 'x-request-id': 'controlled-fixture-request' } });
};
const checks = {};
let candidateCreated = false;
const invoke = (fn, options = {}, signal = new AbortController().signal) => fn(
  'not-a-real-credential', { model: 'controlled-model', input: 'Controlled public lookup', ...options }, signal);
try {
  await writeFile(candidatePath, candidate, { flag: 'wx' });
  candidateCreated = true;
  const original = await import(pathToFileURL(modulePath).href);
  const modified = await import(pathToFileURL(candidatePath).href);
  const baseline = await invoke(original.streamResponse, { webSearch: true, tools: [{ type: 'web_search' }] });
  assert.equal(requests.at(-1).tools, undefined);
  assert.equal(baseline.text, reply);
  assert.equal(baseline.sources, undefined);
  checks.upstream_drops_tools_and_sources = 'passed';

  const researched = await invoke(modified.streamResponse, { webSearch: true });
  assert.deepEqual(requests.at(-1).tools, [{ type: 'web_search' }]);
  assert.deepEqual(requests.at(-1).include, ['web_search_call.action.sources']);
  assert.equal(requests.at(-1).store, false);
  assert.equal(requests.at(-1).stream, true);
  assert.equal(requests.at(-1).max_tool_calls, undefined);
  assert.equal(researched.text, reply);
  assert.equal(researched.searched, true);
  assert.deepEqual(researched.sources, [{ url: source.url, title: source.title }]);
  checks.candidate_tools_and_deduplicated_sources = 'passed';

  const disabled = await invoke(modified.streamResponse);
  assert.equal(requests.at(-1).tools, undefined);
  assert.equal(requests.at(-1).include, undefined);
  assert.deepEqual(disabled.sources, []);
  assert.equal(disabled.searched, false);
  checks.normal_request_unchanged = 'passed';

  scenario = 'no_search';
  const noSearch = await invoke(modified.streamResponse, { webSearch: true });
  assert.equal(noSearch.searched, false);
  assert.deepEqual(noSearch.sources, []);
  checks.no_search_not_claimed_as_search = 'passed';

  scenario = 'unsafe_sources';
  const filtered = await invoke(modified.streamResponse, { webSearch: true });
  assert.deepEqual(filtered.sources, [{ url: source.url, title: source.title }]);
  checks.unsafe_sources_rejected = 'passed';

  scenario = 'failed';
  await assert.rejects(invoke(modified.streamResponse, { webSearch: true }));
  checks.server_denial_not_hidden = 'passed';
  scenario = 'interrupted';
  await assert.rejects(invoke(modified.streamResponse, { webSearch: true }), error => error.code === 'stream_interrupted');
  checks.incomplete_stream_rejected = 'passed';
  const aborted = new AbortController(); aborted.abort();
  await assert.rejects(invoke(modified.streamResponse, { webSearch: true }, aborted.signal), error => error.code === 'cancelled');
  checks.cancelled_request_rejected = 'passed';
} finally {
  globalThis.fetch = savedFetch;
  if (candidateCreated) await unlink(candidatePath).catch(error => { if (error.code !== 'ENOENT') throw error; });
}
console.log('SIWC_WEB_CONTRACT_PROBE=' + JSON.stringify({
  pinned_source_verified: true, actual_sdk: true, mock_transport: true,
  live_account_verified: false, live_search_verified: false, plan_coverage_verified: false,
  credentials_used: false, candidate_removed: true, checks,
}));
