# Phase / Release Implementation Readiness Matrix — v2.0.1

Every release is implemented in its own `release/<release-id>` worktree from synchronized `develop` and merged only after real source-system E2E on the exact final HEAD.

| Order | Release | Phase | Feature/outcome | Existing Golden coverage | Delivery readiness |
|---:|---|---:|---|---:|---|
| 1 | `P1-R01` | 1 | Kernel/Pack repository + contract + Capability Registry foundation | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 2 | `P1-R02` | 1 | Deterministic policy foundation | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 3 | `P1-R03` | 1 | Databricks SQL Warehouse/API connectivity | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 4 | `P1-R04` | 1 | Financial/enterprise connectivity with no-CUR fallback | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 5 | `P1-R05` | 1 | Evidence and baseline configuration foundation | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 6 | `P1-R06` | 1 | TTM-365 cost baseline with explicit AWS evidence quality | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 7 | `P1-R07` | 1 | Cost-based T1–T4 workload/value tiering | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 8 | `P1-R08` | 1 | Core workload/performance evidence | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 9 | `P1-R09` | 1 | Statistical candidate modeling foundation | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 10 | `P1-R10` | 1 | Candidate and independent economics | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 11 | `P1-R11` | 1 | Capacity + auto-stop optimization | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 12 | `P1-R12` | 1 | Eligibility/reliability/advanced single-warehouse evidence | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 13 | `P1-R13` | 1 | Warehouse type + Photon optimization | 4 | READY — worktree + tests + real-source E2E + merge gate |
| 14 | `P1-R14` | 1 | Spot + protective timeout optimization | 3 | READY — worktree + tests + real-source E2E + merge gate |
| 15 | `P1-R15` | 1 | DecisionContext + immutable PlanState + standalone/portfolio orchestration | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 16 | `P1-R16` | 1 | Bounded search, pruning + context-change-driven selective authoritative reevaluation | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 17 | `P1-R17` | 1 | Sequenced and authoritative portfolio economics | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 18 | `P1-R18` | 1 | Deterministic authoritative plan selection | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 19 | `P1-R19` | 1 | Immutable actionable recommendation package | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 20 | `P1-R20` | 1 | Forward + realized-value statistical counterfactuals | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 21 | `P1-R21` | 1 | Forward, realized and protective financial modes | 4 | READY — worktree + tests + real-source E2E + merge gate |
| 22 | `P1-R22` | 1 | Closed-loop lifecycle + change detection + context reconstruction | 9 | READY — worktree + tests + real-source E2E + merge gate |
| 23 | `P1-R23` | 1 | Complete Phase-1 local weekly/selective/all-warehouse product flow + inspectable portfolio report | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 24 | `P1-R24` | 1 | **Phase-1 production/value proof gate — all warehouses inspectable** | 38 | READY — worktree + tests + real-source E2E + merge gate |
| 25 | `P2-R01` | 2 | Unity Catalog Delta + DAB/Lakeflow + Registry/DecisionContext persistence foundation | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 26 | `P2-R02` | 2 | Analyzer PySpark/Delta parity | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 27 | `P2-R03` | 2 | Estimator/Tiering Delta persistence parity | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 28 | `P2-R04` | 2 | Statistical Modeler PySpark parity | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 29 | `P2-R05` | 2 | Optimizer/Orchestrator distributed-backend parity | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 30 | `P2-R06` | 2 | Decision/Recommendation/Lifecycle Delta parity | 0 | READY — worktree + tests + real-source E2E + merge gate |
| 31 | `P2-R07` | 2 | **PySpark/Delta parity gate** | 3 | READY — worktree + tests + real-source E2E + merge gate |
| 32 | `P2-R08` | 2 | ML governance/model registry foundation | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 33 | `P2-R09` | 2 | Selective ML champion activation | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 34 | `P2-R10` | 2 | **Phase-2 complete gate** | 5 | READY — worktree + tests + real-source E2E + merge gate |
| 35 | `P3-R01` | 3 | Intelligence Review foundation — contracts, persistence, model client, tracing, policy | 10 | READY — worktree + tests + real-source E2E + merge gate |
| 36 | `P3-R02` | 3 | Deterministic AgentReviewRouter AR0–AR4 | 3 | READY — worktree + tests + real-source E2E + merge gate |
| 37 | `P3-R03` | 3 | Bounded immutable Agent Evidence Packet | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 38 | `P3-R04` | 3 | Explainer + separately versioned NarrativeExtension | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 39 | `P3-R05` | 3 | Investigator shadow review | 3 | READY — worktree + tests + real-source E2E + merge gate |
| 40 | `P3-R06` | 3 | Challenger shadow falsification | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 41 | `P3-R07` | 3 | Deterministic Review Adapter + typed request seam | 1 | READY — worktree + tests + real-source E2E + merge gate |
| 42 | `P3-R08` | 3 | Capability-gap + ML statistical-fallback integration | 5 | READY — worktree + tests + real-source E2E + merge gate |
| 43 | `P3-R09` | 3 | Adversarial evaluation + AI cost governance | 11 | READY — worktree + tests + real-source E2E + merge gate |
| 44 | `P3-R10` | 3 | Optional controlled reviewer-readiness gating | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 45 | `P3-R11` | 3 | **Phase-3 Intelligence Review complete gate** | 27 | READY — worktree + tests + real-source E2E + merge gate |
| 46 | `P4-R01` | 4 | SQL Warehouse Deep Diagnostic source contract + governed persistence | 3 | READY — worktree + tests + real-source E2E + merge gate |
| 47 | `P4-R02` | 4 | Deterministic diagnostic feature extraction + Analyzer/Modeler enrichment | 3 | READY — worktree + tests + real-source E2E + merge gate |
| 48 | `P4-R03` | 4 | Intelligence Review deep-diagnostic extension | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 49 | `P4-R04` | 4 | Diagnostic lineage through Decision/Recommendation/Lifecycle + optional Query Profile JSON augmentation | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 50 | `P4-R05` | 4 | **Phase-4 Deep Diagnostic Intelligence complete gate** | 4 | READY — worktree + tests + real-source E2E + merge gate |
| 51 | `P5-R01` | 5 | Topology capability/policy/context activation | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 52 | `P5-R02` | 5 | Multi-warehouse affinity evidence | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 53 | `P5-R03` | 5 | Topology counterfactual model | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 54 | `P5-R04` | 5 | Multi-warehouse financial aggregation | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 55 | `P5-R05` | 5 | O6 Warehouse Topology optimizer | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 56 | `P5-R06` | 5 | Structural search + downstream target-warehouse reevaluation | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 57 | `P5-R07` | 5 | Topology decision/package/lifecycle/runtime | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 58 | `P5-R08` | 5 | **Phase-5 topology complete gate** | 2 | READY — worktree + tests + real-source E2E + merge gate |
| 59 | `P6-R01` | 6 | Phase-6 Copilot/tool design + permission/evaluation gate | 3 | BLOCKED — Phase-6 detailed TSD/security/eval prerequisite |
| 60 | `P6-R02` | 6 | Read-only Portfolio Copilot | 1 | BLOCKED — Phase-6 detailed TSD/security/eval prerequisite |
| 61 | `P6-R03` | 6 | Bounded typed evidence-tool pilot | 1 | BLOCKED — Phase-6 detailed TSD/security/eval prerequisite |
| 62 | `P6-R04` | 6 | Optional scheduled-agent bounded tools — independently gated | 1 | BLOCKED — Phase-6 detailed TSD/security/eval prerequisite |
| 63 | `P6-R05` | 6 | **Phase-6 controlled intelligence-access gate** | 3 | BLOCKED — Phase-6 detailed TSD/security/eval prerequisite |
