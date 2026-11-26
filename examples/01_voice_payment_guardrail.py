#!/usr/bin/env python3
"""Example 01: Real-Time Voice Payment Guardrail (< 2 µs per step, < 200 ms turn budget).

Demonstrates capability monotonicity Caps(child) <= Caps(invoker) and cryptographic
ledger chaining: approves a valid transfer in microseconds and blocks an LLM
privilege-escalation attempt ('payments:wire:unlimited') before execution.
"""
from __future__ import annotations
import hashlib, json, time

INVOKER_CAPS = {"payments:transfer:max_500", "contacts:read"}


def jcs(obj) -> str:
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, float)):
        return json.dumps(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, list):
        return "[" + ",".join(jcs(x) for x in obj) + "]"
    keys = sorted(obj.keys(), key=lambda s: s.encode("utf-16-be"))
    return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{jcs(obj[k])}" for k in keys) + "}"


def verify_and_seal_step(step_name: str, requested_caps: set[str], payload: dict, prev_art: str) -> dict:
    t0 = time.perf_counter()
    if not requested_caps.issubset(INVOKER_CAPS):
        dt_us = (time.perf_counter() - t0) * 1e6
        return {"ok": False, "blocked_caps": sorted(requested_caps - INVOKER_CAPS), "latency_us": round(dt_us, 2)}
    atom = {
        "jos": {"kind": "atom", "version": "2.5.0"},
        "meta": {"name": step_name, "version": "0.1.0"},
        "security": {"permissions": sorted(requested_caps), "prev_receipt": prev_art},
        "intention": payload,
        "integrity": {"hash": "", "signature": ""},
    }
    digest = hashlib.sha256(jcs(atom).encode("utf-8")).hexdigest()
    dt_us = (time.perf_counter() - t0) * 1e6
    return {"ok": True, "art_id": f"art_{digest}", "latency_us": round(dt_us, 2)}


if __name__ == "__main__":
    ok_res = verify_and_seal_step(
        "voice-pay-coffee", {"payments:transfer:max_500"},
        {"to": "Cafeteria Roma", "amount_mxn": 89}, "art_genesis"
    )
    blocked_res = verify_and_seal_step(
        "voice-hallucinated-wire", {"payments:wire:unlimited"},
        {"to": "offshore-acct", "amount_mxn": 950000}, ok_res["art_id"]
    )
    print("1. Valid Voice Payment:", json.dumps(ok_res))
    print("2. Escalation Blocked :", json.dumps(blocked_res))
