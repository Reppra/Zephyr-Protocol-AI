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
