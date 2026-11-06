# .jos — declare what an AI agent must achieve, how you will know it is done, and what it must never do

**Start here.** This is the front door of the `.jos` open standard and its community.

AI agents today receive instructions as free text. Nobody can check, before the run, what the agent was asked to do, when it should stop, or what it was forbidden to touch; and nobody can prove afterwards that it complied. `.jos` fixes that with one small JSON document per intention:

- **`intention`** — the objective and the success criteria that a machine can check.
- **`guardrails`** — what to avoid and the hard limits (seconds, output, retries, budget).
- **`execution`** — which engine runs it (a shell, an LLM, a function or a human) and how.

A `.jos` document is data, never code: parsing or validating it runs nothing. A runtime decides whether to act on it and applies its own authorization, sandbox and budget. That single rule is what lets teams share, review, sign and audit agent work the way they already review code.

## Try it in one minute

```bash
npx @josfox/jos verify      # runs the embedded hello.jos through the kernel: SYSTEM HEALTHY
npm install -g @josfox/jos
jos init hello              # writes hello.jos, a 2.0 atom validated by the kernel
jos run hello.jos           # the verdict of each criterion, the run id, a metrics line
jos ledger verify <run_>    # every hash recomputed, chain continuous, run ended
```

Prefer Python? `pip install jos-core` gives the same kernel (`jos-core validate|run …`), same `art_`, same receipts, same ledger bytes.

## What a .jos looks like

An atom with a budget, sealed by its hash:

```json
{
  "jos": { "version": "2.0.0", "kind": "atom" },
  "id": "hello",
  "meta": { "name": "hello", "version": "1.0.0" },
  "intention": {
    "objective": "Say hello and prove it",
    "success_criteria": [ { "exit": 0 }, { "stdout_contains": "hello:ok" } ]
  },
  "guardrails": {
    "avoid": ["network", "writing files"],
    "limit": { "seconds": 10, "output_bytes": 65536, "tokens": 1000, "cost_usd": 0.01, "retries": 0 }
  },
  "security": { "permissions": ["engine:shell", "net:none"] },
  "execution": { "engine": "shell", "run": ["sh", "-c", "echo hello:ok"] },
  "integrity": { "hash": "sha256:41deb162c4a96d87acbdb10dc41f756b6bf2d1872f21024e443697739210db00" }
}
```

`jos run` on this document: code 0, both criteria `pass`, run id `run_…`, artifact `art_41deb162…` (the same hex as the hash). Change one byte of `execution.run` and keep the hash: the kernel refuses to run it, code 3, `integrity: declared hash does not match the computed hash`.

## Why you can trust it

- **A media type in IANA review.** `application/vnd.jos+json` was submitted under RFC 6838; IANA ticket #1460136 is pending.
- **Two independent kernels, one result.** The JavaScript and Python reference kernels each pass 279 of 279 document-level conformance vectors, and the full runner passes 7179 of 7179 checks (measured 2026-10-22, offline).
- **Promises with receipts.** The specification lists 48 promises; 23 are delivered in 2.0 and 6 in part, each tied to the vectors that prove it.
- **Backward compatible.** Every valid 1.0.0 document is a valid 2.0.0 document.
- **Zero dependencies** in both reference kernels.
- **Every command on this page was run** on the published packages on 2026-11-05; the ids and codes shown are the ones they printed.

## Concepts

| Term | Meaning | Defined in |
|---|---|---|
| **intention** | objective + success criteria + what to avoid: the minimum unit | spec §3 |
| **atom · flow · directory · template · crystal · persona · engine** | the document kinds; a kind is inferred when absent | spec §4 |
| **guardrails.limit** | `seconds` (code 124), `output_bytes` (137), `tokens`, `cost_usd`, `retries`; in a flow or folder the effective limit is the element-wise minimum of own, parent remaining and Capability | spec §3.5 |
| **permissions** | `engine:<class>`, `fs:read\|write:<path>`, `net:none\|egress:<host>`, `vault:read:<name>`, `storage:…`, `clone:…` | capability §4 |
| **Capability** | nothing runs without one; a child Capability never widens the parent's | companions/capability |
| **receipt · ledger** | one receipt per step with every criterion's verdict and the hashes of input and output; one append-only, hash-chained ledger per run | spec §7 |
| **art_ · ent_ · run_ · job_ · cap_ · clone_ · blob_** | JOSID: content ids (`art_` = sha256 of the canonical document), stable names (`ent_`), minted ULIDs for runs, jobs, capabilities, clones | companions/josid |
| **crystal** | a sealed record of one execution, served instead of re-running when the key matches | spec §8.3 |
| **foxtail** | a service as a folder: `manifest.jos` + `intentions/` + `gates/`, installed into a scope | profile foxtail/1 |
| **ALAIA agent** | a `usr_` with an owner and a persona document; engaged on a document of the scope under a `job_`; its state is read only from ledgers | services/alaia |

Exit codes, the same everywhere: `0` done · `1` not done · `2` invalid document · `3` blocked (an `avoid` matched, a hash mismatch, a denied Capability, a locked vault) · `4` budget not positive · `5` valid but unexecutable (unresolved `use`, an engine this kernel does not run, no vault opener) · `124` time limit · `137` output limit or kill · `64` usage.

## Create and run

Every command below was run on the published packages; the ids shown are the ones they printed.

### An atom

```bash
jos init greet && jos validate greet.jos --strict && jos run greet.jos
jos runs                   # every run, newest first
jos meter <run_>           # tokens, cost, approvals, denials, cache hits
jos ids greet.jos          # art_ (content) and ent_ (stable name)
```

Inputs come from `--input '{…}'`; defaults declared in `execution.inputs` are not applied at run time, pass every value. A secret is never written in a document: declare `"inputs": { "key": "jos://vault/openai/api_key" }` with the permission `vault:read:openai/api_key`; `jos run` opens the vault and the value reaches the step on stdin, never argv, stdout or the ledger (`jos secrets set openai/api_key`).

### A flow, with a shadow clone

```json
{
  "jos": { "version": "2.0.0", "kind": "flow" }, "id": "shadow", "meta": { "name": "shadow", "version": "0.1.0" },
  "intention": { "objective": "Run one step as a shadow clone", "success_criteria": [ { "exit": 0 }, { "stdout_contains": "clone:ok" } ] },
  "guardrails": { "limit": { "seconds": 20, "cost_usd": 0.10 } },
  "orchestration": {
    "definitions": {
      "worker": {
        "jos": { "version": "2.0.0", "kind": "atom" }, "id": "shadow.worker", "meta": { "name": "worker", "version": "0.1.0" },
        "intention": { "objective": "Work inside the clone", "success_criteria": [ { "stdout_contains": "clone:ok" } ] },
        "guardrails": { "limit": { "seconds": 5, "cost_usd": 0.02 } },
        "execution": { "engine": "shell", "run": ["sh", "-c", "echo clone:ok"] },
        "x-clone": true, "as": "w"
      },
      "report": { "engine": "shell", "run": ["cat"], "needs": ["worker"], "with": { "from_clone": "{{ w }}" } }
    },
    "flows": { "main": { "steps": ["worker", "report"] } }
  }
}
```

`jos run shadow.jos` → code 0. The `worker` receipt carries `clone_…` and its own `run_`; its ledger is `<run_>/clones/<clone_>/ledger.jsonl` with a Capability derived from the flow's and a share of the remaining budget. `jos graph shadow.jos` prints the DAG. Shadow clones run in the JavaScript kernel today; the Python kernel runs the step inline (see [Status](#status-what-ships-today)).

### Cache a result

```bash
jos-core run hello.jos --cache allow         # first run executes and seals a crystal
jos-core run hello.jos --cache allow         # second identical run: cache_hit, served in ~1 ms, no process spawned
jos-core run hello.jos --cache replay-only   # serves a hit, refuses a miss with code 3
```

Caching is opt-in per run; a run that read the vault is never cached.

### A service (a foxtail)

```
hello-service/
  manifest.jos            kind directory, profiles ["foxtail/1","projects/1"], flows main and gates, x-foxtail {name, version, ent, prj, kind, intentions[]}
  intentions/hello.jos    an atom with its own criteria, limits and permissions
  gates/schema.jos        id "hello-service.schema": code that proves a criterion (here: every .jos of the folder validates)
```

```bash
foxctl run intentions/hello.jos          # hello:ok
foxctl run manifest.jos --flow gates     # schema:ok
jos-core hash .                          # the directory hash: the identity of the folder

printf 'password\n' | jos home new eco   # an ecosystem: owner usr_, host_, runtime rt_, an empty vault, policy "allow owner *"
export JOS_HOME=~/.jos-eco
jos projects new hello-service           # prj_… — a foxtail is a project: put it in x-foxtail.prj
jos foxtail add ./hello-service          # validates, copies to .jos/foxtails/<name>/, records owns, part_of, may_use
jos foxtail check hello-service          # 0: the subject may use it now
```

Three rules the installer enforces: a gate id is `<foxtail>.<stem>`; a foxtail is a project; its needs must be a subset of what the installer may grant.

### An agent (ALAIA)

```bash
jos agents new reviewer --owner <usr_>
jos agents write reviewer --with '{"name":"reviewer","objective":"…","system_prompt":"…","rubric_text":"…","threshold":0.8}'
jos agents check reviewer --release                           # usr, owner, persona art_, defined_by, part_of, owns, graph: ok
jos agents engage reviewer --offer .jos/flows/review.jos --budget-usd 0.5    # the offer is a document path of the scope; mints job_
jos run .jos/flows/review.jos --job <job_>                    # the run's ledger is the agent's evidence
jos agents release <job_>
jos agents export reviewer --to antigravity|codex|claude-code|grok   # the same persona rendered for the tool that runs it
```

### Where things live

```
~/.jos/ or ~/.jos-<eco>/   the home: owners registry (usr_ host_ rt_), vault envelope, credentials, runs/<run_>/ledger.jsonl
<scope>/.jos/              manifest.jos, auth/policy.jos, genesis/registries/, flows/ tests/ process/ runbooks/ agents/,
                           projects/<prj_>/, foxtails/<name>/, replays/<run_>/, crystals/
```

## Native to MCP and A2A

`.jos` does not replace the agent protocols; it is the contract they carry.

- **MCP**: `jos serve --mcp` is an MCP server over stdio. Its tools list, read and search files under a root and run a `.jos` through the kernel (`run_document`) with its capabilities, limits and ledger; there is no shell tool. `jos-cli mcp --hub <name>` bridges any MCP client to a hub (`hub_send`, `hub_get`).
- **A2A**: `jos serve --http` publishes an agent card at `/.well-known/agent.json` and accepts tasks at `POST /a2a/tasks/send` (body `payload_type: application/vnd.jos+json`, `payload: <a .jos>`) and `GET /a2a/tasks/get?id=run_…`, each gated by the same policy, Capability and ledger as a local run. `jos-cli hub send|get` is the client.
- **Spec**: `execution.bindings.a2a` and `.mcp` are format members; the `a2a-binding` conformance vector passes on both kernels.

`jos serve` refuses a scope without an owner and an auth policy (`jos auth policy init`), and refuses to bind off loopback without a credential and TLS. That is by design.

## Status: what ships today

Measured on the published packages, 2026-11-05. Honest by design: the specification promises more than the kernels deliver yet, and this table is the line between the two.

| Area | Delivered | Not yet |
|---|---|---|
| Format, validation, normalization of 0.0.7 / 1.0.0 / 1.1.0 | ✔ both kernels | |
| Content ids `art_`, `ent_`, minted ids, directory hash | ✔ | |
| Receipts, hash-chained ledger, `jos ledger verify`, `jos meter` | ✔ | signed ledger seal; a shell step reports no tokens |
| Capability: nothing runs without one, children only narrow | ✔ local-trusted | signed Capabilities, policy layering |
| Flows: DAG, `needs`/`with`/`as`, human gates, templates, `use` with integrity check | ✔ | registries beyond the local library |
| Shadow clones (`x-clone`) with own ledger, budget share, kill | ✔ JS kernel | Python kernel runs the step inline |
| Crystals: second identical run served from cache (`--cache allow`) | ✔ shell steps | model/temperature/seed in the key; crystallized folders; replay modes |
| Engines | `shell`, `jos` | `llm`, `judge`, `function`, `human`: valid documents, code 5 until a later phase |
| Decomposition | step 0 (match) | the other phases |
| Directories: scope, inheritance, `effective` | ✔ | |
| Foxtails: add, enable, check, `foxctl` | ✔ | |
| ALAIA agents: new, write, versions, check, engage, release, export | ✔ | A/B, canary, grading |
| `jos serve`: HTTP screens, MCP server, A2A card and tasks, closed ACL | ✔ | sandbox isolation (`tier: sandbox` is code 5) |
| Hub client: pairing, `hub send\|get`, MCP bridge | ✔ | the rest of the `jos-cli` verb list is specified, not built |
| Graph of facts, PAL storage/blob | ✔ experimental | PAL vault/db/store adapters |

## Pick your path

| You are | Go to |
|---|---|
| Building with agents | `npm install @josfox/jos` or `pip install jos-core`, then the examples in the specification |
| Writing `.jos` in an editor | The [JOSFOX – JOS Open Standard extension](https://marketplace.visualstudio.com/items?itemName=JOSFOX.josfox-jos) for VS Code, Cursor, Windsurf and Antigravity: schema validation and a `jos` MCP server for your editor's agent |
| Implementing the format | The [normative specification, schemas and conformance kit](https://github.com/josfox-jos/jos-spec) |
| Reviewing the registration | [`IANA.md` in the specification repository](https://github.com/josfox-jos/jos-spec/blob/main/IANA.md) |
| Running agents in production | A JOSFOX account at [josfox.cloud](https://josfox.cloud): hosted runtime and services built on `.jos` by JOSFOX LLC |

## Packages

| Tool | What it is | Get it |
|---|---|---|
| [@josfox/jos-core](https://www.npmjs.com/package/@josfox/jos-core) | Reference kernel in JavaScript: validates and runs `.jos`, a receipt per step and a ledger per run. Zero dependencies, no network. 2.1.0 | `npm install @josfox/jos-core` |
| [jos-core](https://pypi.org/project/jos-core/) (Python) | The same kernel in Python, same ids and ledgers. 2.1.0 | `pip install jos-core` |
| [@josfox/jos](https://www.npmjs.com/package/@josfox/jos) | The `jos` command line: documents, runs, ledger, meter, projects, agents, foxtails, secrets, `jos serve` (HTTP, MCP, A2A). 6.0.1 | `npm install -g @josfox/jos` |
| [@josfox/jos-cli](https://www.npmjs.com/package/@josfox/jos-cli) | Client of `.jos` hubs: pair a device, `hub send\|get` over A2A, MCP bridge. 2.0.0 | `npm install -g @josfox/jos-cli` |
| [josctl](https://www.npmjs.com/package/josctl) | Controller: plans, kinds, lifecycle, deploys with rules, desired state. 2.1.1 | `npm install -g josctl` |
| [josfox](https://www.npmjs.com/package/josfox) | Where a person starts: `josfox kickoff` lists your `.jos` scopes and published adapters. 2.1.1 | `npm install -g josfox` |
| [foxctl](https://www.npmjs.com/package/foxctl) · [@josfox/foxctl](https://www.npmjs.com/package/@josfox/foxctl) | Services CLI: find, check and run the `.jos` documents of a service. 2.1.1 | `npm install -g foxctl` |
| [foxjos](https://www.npmjs.com/package/foxjos) | npx runner for `@josfox/jos`. 0.2.1 | `npx foxjos` |
| [VS Code extension](https://marketplace.visualstudio.com/items?itemName=JOSFOX.josfox-jos) | `.jos` for VS Code, Cursor, Windsurf and Antigravity: schema validation and the jos console. 2.1.0 | Visual Studio Marketplace |

Every tool embeds `hello.jos`, so the first run is one command.

## For agents

Load, in this order: [`llms.txt`](llms.txt) (vocabulary, commands, exit codes, where things live), [`AGENTS.md`](AGENTS.md) (how to work inside a `.jos` scope), then the specification. Every claim above was produced by running the packages; an agent that follows `llms.txt` can reproduce each one.

## Releases

| Version | Date | What changed |
|---|---|---|
| 2.1.1 | 2026-11-04 | `josctl` answers clearly when a kernel has no catalog; Apache-2.0 and working links on every package; `@josfox/jos` 6.0.1. |
| 2.1.0 | 2026-10-30 | `jos-core` 2.1.0 on npm and PyPI, `@josfox/jos` 6.0.0, `@josfox/jos-cli` 2.0.0, `josctl`, `josfox` and `foxctl` 2.1.0, VS Code extension 2.1.0. |
| 2.0.0 | 2026-10-22 (spec) · 2026-10-23 (`jos-core` 2.0.0 on npm) | The 2.0.0 specification, an additive superset of 1.0.0; `jos-core` 2.0.0. |

Watch or star this repository: new tools and extensions are announced here.

## The `.jos` community

Ask questions, propose changes and report problems in the [specification issues](https://github.com/josfox-jos/jos-spec/issues). Changes to the format follow the specification's `GOVERNANCE.md`.

Feedback on the tools: [open an issue here](https://github.com/josfox-jos/jos/issues). Security reports: `SECURITY.md` in the specification repository.

## A note from the author

I have done my best to give you a high-quality product. It is still in development, so if you find it useful, enjoy it, and any feedback is very welcome.

This is for you.

Jos

<!-- jos-family:begin -->

## Everything connected to .jos

**The open standard**
- [jos-spec: the normative text, JSON Schemas and test kit](https://github.com/josfox-jos/jos-spec) — the source of truth this page summarizes.
- [jos.mx: the public landing page of the standard](https://github.com/josfox-jos/jos.mx) — the short version for first-time visitors.
- [jos-format-spec: the 0.0.7 draft that started it](https://github.com/josfox-ai/jos-format-spec) — kept for history and for reading old documents.
- [A2A.jos: Agent2Agent protocol fork for carrying `.jos` contracts](https://github.com/josfox-ai/A2A.jos) — where `.jos` meets agent-to-agent transport.
- [.jos-a2a-js: A2A JavaScript SDK fork for `.jos` interoperability](https://github.com/josfox-ai/.jos-a2a-js) — the JavaScript side of that work.

**Built by JOSFOX**
- [josfoxai-deep-link: open the JOSFOX AI app from any web page](https://github.com/josfox-ai/josfoxai-deep-link) — a JOSFOX product utility.
- [josfoxai-deep-link (josfox-jos): pointer to the canonical deep-link helper](https://github.com/josfox-jos/josfoxai-deep-link) — reserved name, no code.

---

Specification text CC BY 4.0, code Apache-2.0. `.jos` is maintained by JOSFOX LLC as change controller, in the open. [josfox.ai](https://josfox.ai) · [josfox.cloud](https://josfox.cloud)

## Public platform documentation — expanded ecosystem

For readers of `josfox-jos/jos`, distribution status per platform is documented in one public hub; its existence does not imply a downloadable artifact or verified host compatibility.

- For readers of `josfox-jos/jos`, [jos-omni](https://github.com/josfox-ai/jos-omni) provides distribution documentation hub.
