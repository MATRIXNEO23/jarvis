"""Execute an approved plan with revocable authorization."""
from __future__ import annotations
from collections.abc import Callable
from threading import Event, Lock
from action_planner import ApprovedPlan

def run_approved_plan(
    plan: ApprovedPlan,
    engine,
    execution_lock: Lock,
    cancel_event: Event,
    abort_event: Event,
    notify: Callable[[tuple], None],
) -> None:
    total = len(plan.steps)
    for index, step in enumerate(plan.steps, start=1):
        if cancel_event.is_set() or abort_event.is_set():
            notify(("finished", "interrotto prima del passo successivo"))
            return
        try:
            with execution_lock:
                if cancel_event.is_set() or abort_event.is_set():
                    notify(("finished", "annullato prima del passo successivo"))
                    return
                result = engine.execute(step.command)
        except Exception:
            notify(("finished", "errore locale interno; arresto prudenziale"))
            return
        notify(("step", index, total, step.description, result.status, result.message,
                str(getattr(result, "task_id", "") or "")))
        if result.status != "completed":
            notify(("finished", "fermato: un passo non è riuscito"))
            return
    notify(("finished", "completato"))
