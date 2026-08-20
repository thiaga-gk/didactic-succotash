# ADR-005 — Lifecycle Manager Owns Lightweight Change Detection

**v2.0.0 disposition:** Retained with v2 terminology: Lifecycle detects/materially classifies changes; DecisionContext determines whether authoritative context changed; Orchestrator performs dependency-directed reevaluation.

**Status:** Proposed with HLA v1.0.0  
**Date:** 2026-08-12

## Context
The product needs to detect applied recommendations, partial applications, configuration drift, and other invalidating changes, but there is no need for a standalone source/data-plane business component.

## Decision
Lifecycle Manager includes lightweight polling/comparison and change classification. Databricks SQL/API/AWS access remains behind infrastructure adapters shared with other components. Core configuration is reconstructed from current system-table state plus API-only fields. Lifecycle compares canonical source/target/current configuration hashes and coordinates context reconstruction; authoritative reevaluation occurs only when DecisionContext/ContextDiff establishes a material change.

## Consequences
- Fewer artificial components.
- One owner for recommendation lifecycle and drift semantics.
- Adapters remain reusable infrastructure, not decision-making services.
