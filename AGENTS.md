# AGENTS.md — working inside a .jos scope

Read `llms.txt` first. These rules are what the kernel and the host enforce; follow them and your work verifies.

## Before you act
1. Find the scope: the nearest `.jos/` upward. Read `.jos/manifest.jos`, `.jos/auth/policy.jos` and `.jos/genesis/registries/owners.json`. If there is no owner of class person, stop and say so: agents and foxtails cannot be created without one.
2. Read the ledgers before the code: `jos runs`, `jos ledger verify <run_>`, `jos meter <run_>`. State comes from verified ledgers, never from a process list or a guess.
3. Resolve ids, do not invent them: `jos ids <file>` for `art_`/`ent_`; a `run_`, `job_`, `cap_`, `clone_` only exists if a ledger or a registry row carries it.

## Writing a document
- Every intention has `success_criteria` and `guardrails.limit`; a criterion is structured (`{exit}`, `{stdout_contains}`, `{stdout_matches}`, `{file_sha256}` …) when it must affect the verdict; free text is descriptive only.
- Declare the minimum permissions: `net:none` unless a host is named with `net:egress:<host>`; one `vault:read:<name>` per secret; never a secret value in a document, argv, stdout, a file or a ledger.
- Seal what you ship: compute `integrity.hash` over the canonical form (JCS) with `integrity.hash` and `integrity.signature` set to empty strings; `art_` is the same hex.
- Validate before running: `jos validate <file> --strict`, then `jos run <file> --dry-run`, then `jos run`. Exit codes: 0 done, 1 not done, 2 invalid, 3 blocked, 5 unexecutable.
- Changing a document changes its `art_`. A new version is a new document beside the old (`jos agents write --next`, `derived_from`), never an overwrite that keeps the old id.
- Do not edit a document so that a gate passes. Fix the work, then re-run the gate.

## Composing
- A flow step that needs its own criteria, limits, permissions or env is an inline document (`jos` + `meta` …); the short `run` form takes none of those.
- Pass every input through `--input`; declared defaults are not applied.
- A step's cwd is its own directory.
- A step marked `"x-clone": true` is a shadow clone: it gets a share of the remaining budget and its own ledger; it cannot widen anything.
- Cache deliberately: `--cache allow` to seal and serve, `--cache replay-only` to forbid execution. Nothing is cached without the flag.

## Agents and services
- An agent is created with `jos agents new` and defined with `jos agents write` from the persona template; `jos agents check <name> --release` must be all `ok` before it is engaged.
- `--offer` is a path to a document the scope indexes (`.jos/flows/…`, `tests/`, `process/`, `runbooks/`, a project's or a foxtail's folders), not a name.
- A foxtail is a project (`x-foxtail.prj`), its gate ids are `<foxtail>.<stem>`, and its needs must fit the installer's grants; `jos foxtail add` refuses otherwise and says which need.
- Export a persona for the tool that runs it (`jos agents export <name> --to antigravity|codex|claude-code|grok`); the export is deterministic and derived from the persona's `art_`.

## Serving
- `jos serve --mcp` exposes files and `run_document`; it never exposes a shell or the home.
- `jos serve --http` needs an owner and `auth/policy.jos`; off loopback it needs a credential and TLS. Do not weaken that to make a demo work.

## What not to claim
- The JS and Python kernels are identical on every conformance vector; shadow clones are JS-only today.
- Engines `llm`, `judge`, `function`, `human` and judged criteria are valid and unexecutable in 2.1 (code 5).
- Metering is real; a shell step reports no tokens.
- A number without its source (a receipt, a ledger entry, a registry row, a vector name) is not a fact.
