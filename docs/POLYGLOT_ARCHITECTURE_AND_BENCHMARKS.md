# `.jos` 2.5.0 Polyglot Architecture, Native `libjos` FFI & Multi-Architecture Benchmark Specification

**Status:** Public Reference Note · **Date:** 2026-11-26 · **License:** CC BY 4.0 (text) / Apache-2.0 (code)  
**Repositories:** [`josfox-jos/jos`](https://github.com/josfox-jos/jos) · [`josfox-jos/jos-spec`](https://github.com/josfox-jos/jos-spec) · [`josfox-jos/libjos`](https://github.com/josfox-jos/libjos) · [`josfox-jos/jos-go`](https://github.com/josfox-jos/jos-go)

---

## 1. Why Sub-10 µs Deterministic `.jos` Execution Matters to Users and the Community

Reporting that in-memory C99/Rust FFI sealing takes **`1.80 µs`** instead of **`6,343.56 µs`** via a CLI subprocess (`3,524×` faster) only matters when connected to concrete problems developers face in production AI systems:

1. **Security & Guardrails with Zero Perceptible Latency (`< 2 ms` per 1,000 Agent Steps)**  
   In real-time voice agents (`< 200 ms` turn budget), IDE copilots, and multi-agent loops, teams frequently disable schema validation, capability checks, or cryptographic audit trails because spawning external validators adds tens or hundreds of milliseconds per tool call. At **`1.80–6.49 µs`** per `.jos` atom in RAM, an orchestrator verifies **1,000 capability-confined tool calls in under `2 ms` total**—making strict safety, `4-JOSID` quorum gates, and hash-chained ledgers effectively free at runtime.

2. **Up to 90% Lower AI Spend via Content-Addressed Crystal Replay (`art_<sha256>`)**  
   Because canonicalizing an intention or context payload under RFC 8785 (JCS) and computing its SHA-256 `art_<hex>` identifier takes microseconds, **FOXTANA** and **ALAIA** fingerprint every normalized prompt, tabular dataset slice, and upstream dependency wave *before* invoking a paid frontier model. When an identical intention crystal has already been verified, the runtime returns the sealed result at **`0` LLM tokens and `$0.00` marginal API cost**.

3. **Lightweight Micro-Services Without Multi-Gigabyte Container Sprawl**  
   Instead of shipping a `1–2 GB` container image for every single-purpose agent or webhook, `.jos` contracts run directly inside a **`~2 MB` static Go binary** (`jos`), a **`~400 KB` C99/Rust shared library** (`libjos`), or an in-process Python ASGI/FastAPI worker (`dotjos`), starting in milliseconds with explicit `security.permissions` and `guardrails.limit`.

4. **One Open Format Across Every Runtime & Screen (`KRMEN` + `ALAIA`)**  
   Just as Git's content-addressed object model freed source code from proprietary version-control servers, `.jos` keeps your AI memory (`Paso Cero`), multi-device UI atoms (`KRMEN`), and multi-agent DAGs (`ALAIA`) portable across **C99, Rust, Go, Python, JavaScript/TypeScript, Swift (macOS/iOS/visionOS), Ruby, and .NET**.

---

## 2. The Five-Layer `.jos` Runtime Stack

| Layer / Package | Responsibility | Primary Invariant |
| :--- | :--- | :--- |
| **`jos` / `jos-core` / `libjos`** | RFC 8785 JCS canonicalization, SHA-256 `art_<hex>` sealing, structural `.jos 2.0` validation, and hash-chained ledgers. | Identical bytes produce the exact same `art_<64-hex>` across C, Rust, Go, Python, and JS. |
| **`josctl` / `foxctl`** | Desired-state control plane, encrypted vault references (`vault://<vendor>/api_key`), 6-stage Foxtail forge, and `4-JOSID` sadmin quorum gates. | High/critical actions require sadmin invoker, confined sadmin agent, JCS payload hash, and fresh human 2FA quorum (`1` or `2` distinct humans). |
| **`krmen`** | Declarative 6-layer UI compiler (`L0` 7-device CSS `@container` shells, `L1` material backdrops, `L2` design tokens, `L3` precompiled components, `L5` interactive FX). | **SG6:** Zero raw color, font, or pixel literals inside components; compiles `desktop`, `tablet`, `ios`, `android`, `foldable_duo`, `kiosk`, and `vr_headset` in `~70 µs`. |
| **`alaia`** | Multi-agent Swarm DAG orchestrator & `A2A` envelope sealer. | **`Caps(child) ⊆ Caps(invoker)`** enforced before wave compilation; deterministic cycle rejection and `$0` warm crystal replay. |
| **`foxtana`** | Sovereign coordinator: `Paso Cero` portable user memory, `SmartOptimizer` context compression, and `AthenaGate` independent delivery audit. | **`Author != Reviewer`** cryptographically enforced on every delivery receipt. |

---

## 3. Reproducible Benchmark Report (2026-11-26)

### Methodology & Hardware
- **Machine:** Apple Silicon (`darwin/arm64`, macOS, Go `1.27.4`, Rust `rustc 1.100.0 -O`, Clang `-O3`, Python `3.12.7`).
- **Workload A (Core Atom Seal):** Construct a `.jos 2.0` `atom` (`jos`, `meta`, `intention`, `integrity`), canonicalize under RFC 8785 JCS, compute FIPS 180-4 SHA-256, and emit sealed JSON + `art_<64-hex>`.
- **Workload B (Full `KRMEN` 7-Device Compilation):** Validate `SG6` token-only declarations on a `hero` component, compile CSS `@container` / posture / spatial rules for all 7 device classes (`desktop`, `tablet`, `ios`, `android`, `foldable_duo`, `kiosk`, `vr_headset`), content-address the stylesheet, and seal the `template.jos` crystal.
- **Fairness Rule:** Offline local execution only; zero third-party vendor estimates.

### Measured Results

| Execution Mode | Workload | Latency / Op (µs) | Throughput (ops/sec) | Speedup vs. CLI Subprocess |
| :--- | :--- | ---: | ---: | ---: |
| **CLI Subprocess** (`subprocess.run(["jos", "verify", …])`) | Workload A (process spawn + file I/O) | `6,343.56 µs` | `~157 / s` | `1.0×` (baseline) |
| **Pure Python In-Memory** (`from jos_py import seal_jos`) | Workload A (deep-copy + UTF-16BE JCS + SHA-256) | `44.19 µs` | `~22,630 / s` | **`143.5×`** |
| **Rust Native** (`jos_core::seal_atom`, dynamic `BTreeMap` AST) | Workload A (full dynamic AST + JCS + SHA-256) | `6.49 µs` | `~154,080 / s` | **`977.4×`** |
| **Go Native In-Memory** (`josfox.cloud/jos.ComputeIntegrityHash`) | Workload A (in-memory JCS + `crypto/sha256`) | `2.50 µs` | `~400,000 / s` | **`2,537.4×`** |
| **Python + `libjos` C99 FFI** (`ctypes` zero-alloc stack buffer) | Workload A (in-memory C99 `jos_seal_atom_buf`) | **`1.80 µs`** | **`~555,550 / s`** | **`3,524.2×`** |
| **`KRMEN` Multi-Device Compiler** (`KrmenBundle.compile()`) | Workload B (7 device shells + CSS hash + `.jos` seal) | **`70.06 µs`** | **`~14,270 / s`** | **`90.5×`** |

> **Architectural Takeaway:** Keep CLI binaries (`jos`, `foxtana`, `josctl`) for terminal workflows, CI gates, and human inspection, while importing the native in-memory libraries (`jos_py` / `libjos`, `josfox.cloud/jos`, `@josfox/jos-core`, `krmen`, `alaia`) inside hot request paths, multi-agent DAGs, and UI servers.

---

## 4. Official Packages & Standalone Binaries

### Package Registries

| Ecosystem | Package(s) | Install Command |
| :--- | :--- | :--- |
| **JavaScript / TypeScript (npm)** | [`@josfox/jos`](https://www.npmjs.com/package/@josfox/jos) · [`@josfox/jos-core`](https://www.npmjs.com/package/@josfox/jos-core) · [`foxtana`](https://www.npmjs.com/package/foxtana) · [`krmen`](https://www.npmjs.com/package/krmen) · [`alaia`](https://www.npmjs.com/package/alaia) · [`athena-jos`](https://www.npmjs.com/package/athena-jos) | `npm install @josfox/jos krmen alaia foxtana` |
| **Python (PyPI)** | [`jos-core`](https://pypi.org/project/jos-core/) · [`dotjos`](https://pypi.org/project/dotjos/) (`jos-py`) · [`josctl`](https://pypi.org/project/josctl/) · [`foxtana`](https://pypi.org/project/foxtana/) · [`josfox`](https://pypi.org/project/josfox/) | `pip install jos-core dotjos josctl foxtana` |
| **Go (`pkg.go.dev`)** | [`josfox.cloud/jos`](https://pkg.go.dev/josfox.cloud/jos) · [`josfox.cloud/foxtana`](https://pkg.go.dev/josfox.cloud/foxtana) · [`josfox.cloud/krmen`](https://pkg.go.dev/josfox.cloud/krmen) · [`josfox.cloud/alaia`](https://pkg.go.dev/josfox.cloud/alaia) | `go get josfox.cloud/jos@v0.1.2` |
| **C99 / CMake / SwiftPM** | [`josfox-jos/libjos`](https://github.com/josfox-jos/libjos) (`CLibJos` & `JosSwift`) | `.package(url: "https://github.com/josfox-jos/libjos", from: "0.1.0")` |

### Direct Standalone Binaries (`v2.5.0` Release Assets)
All static zero-dependency binaries and `SHA256SUMS.txt` are published at **[GitHub Release `v2.5.0`](https://github.com/josfox-jos/jos/releases/tag/v2.5.0)**:
- macOS Apple Silicon (`arm64`): [`jos-darwin-arm64`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/jos-darwin-arm64) · [`foxtana-darwin-arm64`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/foxtana-darwin-arm64)
- macOS Intel (`amd64`): [`jos-darwin-amd64`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/jos-darwin-amd64)
- Linux (`x86_64` & `arm64`): [`jos-linux-amd64`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/jos-linux-amd64) · [`jos-linux-arm64`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/jos-linux-arm64) · [`foxtana-linux-amd64`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/foxtana-linux-amd64)
- Windows (`x86_64`): [`jos-windows-amd64.exe`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/jos-windows-amd64.exe) · [`foxtana-windows-amd64.exe`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/foxtana-windows-amd64.exe)
- C99 / CMake / SwiftPM Source Tarball: [`libjos-0.1.0-c99-swiftpm.tar.gz`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/libjos-0.1.0-c99-swiftpm.tar.gz)
- Checksums: [`SHA256SUMS.txt`](https://github.com/josfox-jos/jos/releases/download/v2.5.0/SHA256SUMS.txt)

```text
e3944398decb121e3ab610eea7147d8a64cb5a72f4e85340c4294ce82f6f4f36  jos-darwin-amd64
f76085acb8da16fcd192701f0f5b7be8f93d5ab4c7211ece7a8b9b4d32ed9aa4  jos-darwin-arm64
6ea5e2acf5a13564bf557780857dcc6bf769a511e5f49e2d928b907b04939844  jos-linux-amd64
daa77e33d5bd6402ebce4d37149724ac90fba7941eb57e20eb69ba7f6b262dea  jos-linux-arm64
8d87367d341eb2e6c32a4d8d4882f0eaf8f5eb8e99b9c51f7e35c0f10a97c0d2  jos-windows-amd64.exe
a28464ce2ef7946f1051ae8eef9909c5495f4580f8d6aef020936492ddd57fc9  foxtana-darwin-arm64
0027f958c03b3a5ada0de6b0d8d842c6f8fbb45d4229cbc27d6c66be3abfe1f6  foxtana-linux-amd64
a37b7afa4cfb66272fd22558a2b6f22adba8a135b2e184b8038701fcedc09624  foxtana-windows-amd64.exe
2147c6efa99935a7114e2a4de966b0f88812a344bf9f16ff5f7ff38fe188947a  libjos-0.1.0-c99-swiftpm.tar.gz
```

