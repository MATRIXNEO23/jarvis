"""Development-only Windows quota protocol probe. No login or model turns."""
from __future__ import annotations
import argparse
import ctypes
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_quota.provider import Provider, QuotaUnavailable


class ProcessRPC:
    ALLOWED = {'initialize', 'account/read', 'account/rateLimits/read'}

    def __init__(self, executable, args, env, cwd):
        self.messages = queue.Queue()
        self.methods = []
        self.next_id = 0
        self.process = subprocess.Popen([str(executable), '--listen', 'stdio://',
            '-c', 'cli_auth_credentials_store="ephemeral"', *args],
            cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
            creationflags=0x08000000)
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        try:
            for line in self.process.stdout:
                if len(line) > 2_000_000:
                    self.messages.put(None)
                    return
                try:
                    message = json.loads(line)
                except ValueError:
                    continue
                self.messages.put(message)
        finally:
            self.messages.put(None)

    def call(self, method, params, *, timeout=10.0):
        if method not in self.ALLOWED:
            raise AssertionError('Forbidden RPC method')
        self.next_id += 1
        ident = self.next_id
        self.methods.append(method)
        self.process.stdin.write(json.dumps(dict(id=ident, method=method, params=params))+'\n')
        self.process.stdin.flush()
        end = time.monotonic()+timeout
        while True:
            message = self.messages.get(timeout=max(.01, end-time.monotonic()))
            if message is None:
                raise RuntimeError('App-server ended before RPC reply')
            if message.get('id') == ident:
                return message
            if 'id' in message and 'method' in message:
                raise AssertionError('Unexpected server request; no automatic auth allowed')

    def initialized(self):
        self.process.stdin.write('{"method":"initialized"}\n')
        self.process.stdin.flush()

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        self.reader.join(timeout=1)


def private_memory(pid):
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize',
            'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    process = kernel.OpenProcess(0x1000 | 0x10, False, pid)
    if not process:
        return None
    try:
        info = Counters(); info.cb = ctypes.sizeof(info)
        api = ctypes.WinDLL('psapi').GetProcessMemoryInfo
        api.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        if not api(process, ctypes.byref(info), info.cb):
            return None
        return dict(working_set_bytes=info.WorkingSetSize, private_bytes=info.PrivateUsage)
    finally:
        kernel.CloseHandle(process)


def native_probe(executable, folder):
    if os.environ.get('CI') != 'true':
        raise RuntimeError('Native no-account probe restricted to disposable CI')
    requests = []
    class Trap(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            requests.append(('GET', self.path))
            self.send_response(503); self.end_headers()
        def do_POST(self):
            requests.append(('POST', self.path))
            self.send_response(503); self.end_headers()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Trap)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        for custom_provider in (False, True):
            # Do not import credentials or change the executor's home variables.
            env = {key:value for key,value in os.environ.items() if
                not key.upper().startswith(('OPENAI_', 'CODEX_', 'CHATGPT_'))}
            args = []
            if custom_provider:
                env['JARVIS_QUOTA_TEST_ACCESS'] = 'fake-not-a-credential'
                args = ['-c', 'model_provider="quota_probe"',
                    '-c', 'model_providers.quota_probe.name="Quota probe"',
                    '-c', 'model_providers.quota_probe.base_url="http://127.0.0.1:'+str(server.server_port)+'/v1"',
                    '-c', 'model_providers.quota_probe.env_key="JARVIS_QUOTA_TEST_ACCESS"',
                    '-c', 'model_providers.quota_probe.wire_api="responses"',
                    '-c', 'model_providers.quota_probe.requires_openai_auth=false']
            started = time.monotonic()
            rpc = ProcessRPC(executable, args, env, folder)
            try:
                reply = rpc.call('initialize', {'clientInfo': {'name':'jarvis_quota_probe',
                    'title':'Jarvis development quota probe', 'version':'0.0.1'}})
                assert 'result' in reply, 'Initialization failed'
                rpc.initialized()
                account = rpc.call('account/read', {'refreshToken':False})
                identity = account.get('result', {}).get('account')
                assert identity is None or (custom_provider and identity.get('type') == 'apiKey'), 'Unexpected connected account'
                reply = rpc.call('account/rateLimits/read', {})
                assert reply.get('error', {}).get('code') == -32600, 'Expected auth-required error'
                assert 'authentication required' in reply['error']['message'], 'Unexpected quota failure'
                # Exercise the product boundary against this real, unconnected server.
                with_error = Provider(rpc, session_key='isolated-no-account')
                try:
                    with_error.read_limits()
                except QuotaUnavailable:
                    pass
                else:
                    raise AssertionError('No-account server was treated as live quota')
                results.append(dict(mode='siwc_provider_shape' if custom_provider else 'no_auth',
                    quota_state='authentication_required', real_account_quota=False,
                    methods=rpc.methods[:], model_turns=0,
                    memory=private_memory(rpc.process.pid),
                    elapsed_seconds=round(time.monotonic()-started, 3)))
            finally:
                rpc.close()
        assert not any(method == 'POST' for method,path in requests), 'Inference HTTP detected'
    finally:
        server.shutdown(); server.server_close()
    return dict(native=True, results=results, loopback_requests=requests,
        binary_bytes=executable.stat().st_size, real_account_quota=False)


def protocol_probe():
    class Fixture:
        def __init__(self): self.methods = []
        def call(self, method, params, *, timeout):
            assert method == 'account/rateLimits/read' and params == {}
            self.methods.append(method)
            return {'result': {'rateLimits': {'limitId':'codex',
                'primary': {'usedPercent':25,'windowDurationMins':300,'resetsAt':2000000000}}}}
    fixture = Fixture()
    result = Provider(fixture, session_key='controlled-fixture').read_limits()
    assert result['rateLimits']['primary']['usedPercent'] == 25
    assert fixture.methods == ['account/rateLimits/read']
    return dict(native=False, fixture=True, methods=fixture.methods,
        model_turns=0, real_account_quota=False)


def main():
    if os.name != 'nt':
        raise SystemExit('Only Windows verification is authorized.')
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--protocol-only', action='store_true')
    mode.add_argument('--codex', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = protocol_probe() if args.protocol_only else native_probe(args.codex.resolve(), args.output.parent.resolve())
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('QUOTA_PROBE='+json.dumps(result))


if __name__ == '__main__':
    main()
