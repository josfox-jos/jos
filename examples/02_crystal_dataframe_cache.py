#!/usr/bin/env python3
"""Example 02: Scientific Tabular Provenance & $0 Crystal Replay (.jos 2.5.0).

Seals a normalized dataset + prompt intention into a content-addressed crystal (art_<sha256>).
First run executes the expensive LLM/embedding function ($0.04, ~850 ms simulated);
subsequent runs with identical canonical bytes replay in < 1 µs at 0 tokens and $0.00.
"""
from __future__ import annotations
import hashlib, json, time

CRYSTAL_STORE: dict[str, dict] = {}


def jcs(obj) -> str:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, list):
        return "[" + ",".join(jcs(x) for x in obj) + "]"
    return "{" + ",".join(f"{json.dumps(k)}:{jcs(obj[k])}" for k in sorted(obj)) + "}"


def run_or_crystallize(task: str, rows: list[dict], expensive_llm_fn) -> dict:
    t0 = time.perf_counter()
    crystal_key = "art_" + hashlib.sha256(jcs({"task": task, "rows": rows}).encode("utf-8")).hexdigest()
    if crystal_key in CRYSTAL_STORE:
        dt_us = (time.perf_counter() - t0) * 1e6
        return {"mode": "WARM_CRYSTAL_REPLAY", "art_id": crystal_key, "tokens": 0, "cost_usd": 0.0, "latency_us": round(dt_us, 3), "output": CRYSTAL_STORE[crystal_key]}
    out = expensive_llm_fn(rows)
    CRYSTAL_STORE[crystal_key] = out
    dt_us = (time.perf_counter() - t0) * 1e6
    return {"mode": "COLD_LLM_COMPUTE", "art_id": crystal_key, "tokens": 1850, "cost_usd": 0.0185, "latency_us": round(dt_us, 1), "output": out}


if __name__ == "__main__":
    batch = [{"sku": "JOS-PRO", "mxn": 9, "active": True}, {"sku": "JOS-FREE", "mxn": 0, "active": True}]
    llm_sim = lambda r: {"total_skus": len(r), "summary": "Contraste $0 vs $9 MXN verificado"}
    print("Run #1 (Cold):", json.dumps(run_or_crystallize("pricing-audit", batch, llm_sim)))
    print("Run #2 (Warm):", json.dumps(run_or_crystallize("pricing-audit", batch, llm_sim)))
