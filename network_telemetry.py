"""Optional real Windows network telemetry for LUMI HUD.

Uses the built-in Windows netstat executable with a fixed read-only
argument list. Runs on a daemon worker, never blocks the Tk event loop,
never executes user input, and never sends network data anywhere.
"""
from __future__ import annotations

import os
from queue import SimpleQueue
import re
import subprocess
import threading
import time


def parse_interface_bytes(text: str):
    """Find cumulative RX/TX octets, including Italian netstat output."""
    if not isinstance(text,str):
        return None
    for line in text.splitlines():
        line=line.strip()
        if not line:
            continue
        parts=line.split()
        if len(parts)<3:
            continue
        if parts[0].casefold().rstrip(":") not in (
                "bytes","byte","octets","octetos"):
            continue
        values=[]
        for part in parts[1:]:
            if re.fullmatch(r"[0-9][0-9,.]*",part):
                values.append(int(part.replace(",","").replace(".","")))
        if len(values)>=2:
            return tuple(values[:2])
    return None


def _query_bytes():
    if os.name!="nt":
        return None
    try:
        flags=getattr(subprocess,"CREATE_NO_WINDOW",0)
        answer=subprocess.run(
            ["netstat.exe","-e"],capture_output=True,text=True,
            timeout=2.5,creationflags=flags,check=False,
            shell=False)
        if answer.returncode!=0:
            return None
        return parse_interface_bytes(answer.stdout)
    except (OSError,ValueError,subprocess.TimeoutExpired):
        return None


def friendly_rate(number):
    """Format a real bytes-per-second counter, not a synthetic Mbps figure."""
    if number is None:
        return "--"
    n=max(0.0,float(number))
    for unit in ("B/s","KB/s","MB/s","GB/s"):
        if n < 1024 or unit=="GB/s":
            return f"{n:.0f}{unit}" if unit=="B/s" else f"{n:.1f}{unit}"
        n/=1024
    return "--"


class NetworkTelemetry:
    def __init__(self):
        self._pending=False
        self._queue=SimpleQueue()
        self._previous=None
        self._last_rates=None

    def request(self):
        """At most one non-blocking Windows statistics request in flight."""
        if self._pending or os.name!="nt":
            return
        self._pending=True

        def worker():
            self._queue.put((time.monotonic(),_query_bytes()))
        threading.Thread(target=worker,daemon=True,
                         name="LUMI-Network-Read").start()

    def result(self):
        while not self._queue.empty():
            when,pair=self._queue.get()
            self._pending=False
            if pair is None:
                self._last_rates=None
                continue
            if self._previous is not None:
                past_time,past=self._previous
                elapsed=when-past_time
                if elapsed>.2:
                    received=max(0,(pair[0]-past[0])/elapsed)
                    sent=max(0,(pair[1]-past[1])/elapsed)
                    self._last_rates=(received,sent)
            self._previous=(when,pair)
        return self._last_rates
