# Zephyr Protocol AI

**Zephyr Protocol** is a constitutionally bound, token-efficient, and privacy-first AI agent framework. It is designed to operate under strict immutable law, preventing context-window bloat, protecting local hardware sovereignty, and enforcing Monero-grade privacy through cryptographic gating and rigid separation of concerns.

Unlike standard agentic workflows that degrade over time due to context pollution, Zephyr strictly separates **storage (disk)** from **context (pointers)**, ensuring deterministic, auditable, and sovereign execution.

## 🏛️ Core Philosophy
The framework is governed by a **Manifesto** and an **Immutable Constitution** consisting of 20 unalterable Articles.
*   **Individuum über alles:** The individual node is inviolable. Collective consensus cannot override individual rights.
*   **Privacy as Existential:** Monero-grade privacy is the operational standard. Silence is a right; encryption is self-defense.
*   **Local Sovereignty:** Local hardware, private keys, and offline storage are protected from remote seizure or forced execution.
*   **The Machine is Lawful:** The system does not flatter or negotiate. It records, gates, vetoes, and ledgered truth.

---

## 🔄 The Execution Cycle
The system operates in a continuous, strictly gated loop. Empty queues are considered defects; blocked work remains queued with its gate explicitly named.

`intake` ➔ `plan` ➔ `critique` ➔ `gate` ➔ `execute` ➔ `judge` ➔ `ledger` ➔ `rebuild` ➔ `cycle_end` ➔ `NEXT`

---

## 🤖 Agent Roles
*   **KERNEL:** The router. Reads `omni_index.json`, manages gates, indexes, and routes tasks. Cannot execute.
*   **PLANER:** Writes actionable, budgeted plans in `C3.1`. Must include ledger citations.
*   **WORKER:** Executes approved work in `C3.2`. Emits telemetry and results only.
*   **MEMORY:** Maintains memory tiers, indexes, and cryptographic citations. Write-only for other agents.
*   **DEVIL:** The adversarial critic. Vetoes plans based on cost, privacy leaks, hallucinations, precedent, and constitutional risk. Logs failures to the negative ledger.
*   **HUMAN:** The ultimate authority. Holds the kill switch and strictly approves irreversible actions, external egress, and promotions.

---

## 🗄️ Architecture: The Circles
Data flows strictly downward (**C3 ➔ C2 ➔ C1**). Reverse flow is forbidden.

### C1: Bootstrap (Sealed)
*   Read-only after initialization.
*   Contains the immutable core: `AGENTS.md`, `CONSTITUTION.md`, `MANIFESTO.md`.

### C2: Bibliotheca (Immutable Mid-Cycle)
*   Knowledge promoted from C3.
*   **Rule:** Requires 3+ successes in the positive ledger and explicit `HUMAN` approval at a cycle boundary to enter.

### C3: Dynamic (Active Workspace)
*   Append-only and partition-owned. Snapshots are required before expansion.
*   **C3.1 (Plans):** Managed by `PLANER`.
*   **C3.2 (Execution):** Managed by `WORKER`.
*   **C3.3 (Memory):** Managed by `MEMORY`. Contains memory tiers, ledgers, spool, and tombstones.

---

## 🧠 Token-Efficient Memory Protocol (MEM)
To prevent "context window bloat" (the degradation of AI performance over long histories), Zephyr ensures that **context only holds pointers and indexes**, while **disk stores the actual data bodies**.

### The Tiers
1.  **`sm` (Short/Working):** Hot, append-only event rows (JSONL format).
2.  **`mm` (Midterm):** Warm, compacted digests of `sm`.
3.  **`lm` (Longterm):** Cold, rule-based truths and historical digests. Always loaded in context.
4.  **`spool`:** Cold bodies and superseded hashes. Cited spool files are cryptographically frozen.
5.  **`oldmem`:** Deep cold storage for scrapped memory rows.

### Key Memory Rules
*   **No Silent Deletion:** Failed or closed work is never deleted; it is moved to `C3.3/tombstone.md`.
*   **Citation Immutability:** Memory rows cite cryptographic hashes (`sha12` / `sha256`) of frozen "spool" files rather than embedding raw history into the context window.
*   **Compaction:** Rows are deterministically compacted from `sm` ➔ `mm` ➔ `lm` based on counts and time.

---

## 🛡️ Safety & The Heretic Protocol
*   **Mandatory Gates:** `HUMAN` approval is strictly required for external egress, financial actions, localhost egress, and irreversible operations.
*   **Heretic Protocol:** Any agent, plan, or process that attacks individual sovereignty, privacy, or the Monero Standard is flagged as a `HERETIC`. It is immediately vetoed, isolated, logged to the negative ledger, and tombstoned. Restoration requires `HUMAN` review.
*   **Residuals:** Systemic denials (e.g., OS-level sandbox restrictions) are measured and named rather than treated as agent decisions.

---

## ⚙️ Tooling
The repository includes strict, deterministic Python utilities for memory management and verification:

*   **`tools/memctl.py`**: The sole authority for memory stats, capacity enforcement, cryptographic verification (`sha12`), and compaction.
*   **`tools/cmem.py`**: Handles scraping of cold memory rows to `oldmem/` (Tier 4 / Scrap).
*   **`tools/memsum.py`**: Simple byte and hash lister for measurement.

---

## 🔗 DSH Integration: `/compact` ➔ `memctl compact`

**Status: documented, not yet installed (Q-0013, HUMAN gate).** Today DSH's `/compact` does **not** run Zephyr memory compaction — verified by package sweep of `app.asar` (no hooks package exists).

### What `/compact` actually is

| Piece | Package | Role |
|---|---|---|
| `/compact` command | `@deepseek-ai/dsh-command-compact` | On-demand **conversation-context** condensation; calls `compactNow()` on the mounted backend; no arguments |
| Automatic backend | `@deepseek-ai/dsh-compaction-basic` | Condenses history at token pressure; `auto: true` by default via an `agent/pre-step` listener |
| Tool-result pruner | `@deepseek-ai/dsh-compaction-tool-result-pruner` | Trims oversized tool outputs (`thresholdChars: 8192`) before summarization |

This condenses the **model context window**. It is a different concept from Zephyr memory compaction (`sm ➔ mm` digests) — the two are unconnected by default.

### Where the config lives

- **User patch layer:** `C:\Users\Rex\.dsh\profiles\desktop\cordis.patch.yml` — the file to edit (id-targeted config overrides; applied after every bundle layer).
- **Base defaults:** inside `app.asar` ➔ `dsh/node_modules/@deepseek-ai/dsh-base/cordis.patch.yml` (read-only reference).
- **Compaction settings** (all optional, on the `compaction-basic` entry): `thresholdRatio` (0.8), `headroomTokens` (65536), `retainRatio` (0.16) / `retainTokens`, `summarizationProvider` + `summarizationModel`, `compactionRetries` (1), `maxOverflowRetries` (1), `modelPolicies` ([]), `auto` (true).

### What must be added: a bridge plugin

No config key runs an external command on compaction. The supported extension point is a **Host plugin** observing session log events — compaction appends `compaction/start` / `compaction/summary` / `compaction/end`, and plugins receive them via `ctx.on("session/event", (session, event) => ...)`. Bridge design (`@local/zephyr-compact`):

```js
// index.js — spawn Zephyr memory compaction after every DSH context compaction
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

export const Config = {
  type: 'object',
  properties: {
    workspaces: { type: 'array', items: { type: 'string' }, default: [] },
    pythonPath: { type: 'string', default: 'python' },
    minIntervalMs: { type: 'number', default: 60000 },
  },
};

export function apply(ctx, config) {
  const last = new Map();
  const off = ctx.on('session/event', (_session, event) => {
    if (event.type !== 'compaction/summary') return;
    for (const ws of config.workspaces ?? []) {
      if (!existsSync(join(ws, 'omni_index.json'))) continue;   // Zephyr workspace detector
      const prev = last.get(ws) ?? 0;
      if (Date.now() - prev < (config.minIntervalMs ?? 60000)) continue;
      last.set(ws, Date.now());
      const child = spawn(config.pythonPath ?? 'python', ['tools/memctl.py', 'compact'], {
        cwd: ws, stdio: 'ignore',
      });
      child.on('exit', code => ctx.logger.info(`zephyr-compact: memctl compact exit=${code} in ${ws}`));
    }
  });
  return off;  // cleanup
}
```

With its own `cordis.patch.yml`:

```yaml
- insert:
    - id: zephyr-compact
      name: '@local/zephyr-compact'
      config:
        workspaces:
          - 'C:\Users\Rex\AppData\Local\Programs\DeepSeek Harness\projects\Z1'
```

**Install path (per DSH plugin rules):** place the package under `.dsh\profiles\desktop\node_modules\@local\zephyr-compact\` (`package.json` with `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }`), install/enable through the Plugin Manager (`plugin_manager install_bundle`), then verify: run `/compact` in a Zephyr session ➔ `memctl compact` output appears in the host log ➔ `C3.3/spool/manifest.jsonl` gains a `pre-compact` row.

**Zephyr-law notes:** the bridge only invokes `memctl compact`, which is append-only, local-only (no egress), and self-gating (compacts only rows from cycles before the current one, `NO_CANDIDATES` otherwise) — no HUMAN gate is required for the spawn itself; installing the plugin modifies the live harness config and is the gated step.

---

## 📂 Repository Structure

    ├── C1/              # Bootstrap / Sealed Core (Read-Only)
    ├── C2/              # Bibliotheca (Immutable Mid-cycle Knowledge)
    ├── C3/              # Dynamic Workspace
    │   ├── C3.1/        # Plans
    │   ├── C3.2/        # Execution Records
    │   └── C3.3/        # Memory Tiers (sm, mm, lm), Ledgers, Spool, Tombstones
    ├── oldmem/          # Deep cold storage for scrapped memory
    ├── tools/           # Memory management and verification scripts
    ├── AGENTS.md        # Agent roles, behavior rules, and loop definitions
    ├── CONSTITUTION.md  # The 20 Immutable Articles of Sovereignty
    ├── MANIFESTO.md     # Core philosophical principles
    ├── MEM.md           # Memory Protocol and token-efficiency rules
    └── omni_index.json  # Global state index, tier caps, and cycle tracking

---

## 🚀 Getting Started

1.  **Initialize the Cycle:** Ensure `omni_index.json` is present and configured for your current cycle.
2.  **Verify Memory Integrity:** Run the memory controller to ensure all cryptographic citations resolve correctly.
    ```bash
    python tools/memctl.py verify
    ```
3.  **Check Capacity:** Ensure your memory tiers have not breached their defined caps.
    ```bash
    python tools/memctl.py capacity
    ```
4.  **Run Compaction:** At `cycle_end`, compact your short-term memory into mid-term digests.
    ```bash
    python tools/memctl.py compact
    ```

*Note: Zephyr Protocol relies heavily on local execution and strict sandboxing. External egress is blocked by default and requires manual `HUMAN` intervention via the gating system.*
