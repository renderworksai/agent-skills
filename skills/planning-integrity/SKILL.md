---
name: planning-integrity
description: Checks the integrity of an existing engineering plan against repository evidence and current architectural decisions. Use when validating an approved design or implementation plan for stale assumptions, historical document conflicts, missing prerequisites, interface ownership, regression dependencies, or acceptance gaps. Excludes authoring a new plan and implementation.
---

# Planning Integrity

## Overview
Validate the evidence and completeness of an existing design or implementation plan without replacing its decisions. Superpowers, when present, retains responsibility for brainstorming, requirements, architecture, specification, planning, and user approval. This skill supplies a focused integrity review within that workflow.

## When to Use
Use for an existing plan whose repository fit, preserved context, or readiness needs checking. First identify whether it is a draft, awaiting approval, approved, or already executing. Review does not grant approval or advance an unapproved stage.

Exclude open-ended requirement discovery, creation of a new architecture or plan, routine conversation, and implementation. If no existing plan is available, identify that missing input without inventing one.

## Process
1. Establish active authority. Read the relevant user decisions, approved scope, repository policy, and plan revision. Distinguish current instructions from historical or superseded documents. A newer timestamp alone does not establish authority; use explicit approval and supersession evidence. Surface unresolved conflicts instead of silently choosing an architecture.
2. Reuse verified findings. Carry forward relevant source revisions, paths, interface observations, resolved questions, and test results. Label observed facts, inferences, and unverified assumptions. Recheck a finding only when changed code, stale provenance, or contradictory evidence materially affects the current decision.
3. Check architecture and interface ownership. Trace proposed changes through the affected modules, producers, consumers, and dependencies. Confirm contracts, compatibility, protected behavior, and existing invariants against cited evidence. An inferred consumer is a question to verify, not a confirmed dependency.
4. Check execution completeness. Look for missing prerequisites, dependency order, regression coverage, required tests, acceptance criteria, and approval boundaries. Connect each material gap to its likely consequence. Existing tests establish only what they actually exercise; require acceptance evidence for protected behavior affected by the proposal.
5. Investigate only material gaps. Inspect the smallest relevant source, policy, or test needed to resolve missing or contradictory evidence. Preserve already settled questions. Do not launch another full-repository audit, brainstorm alternatives, rewrite the plan, or implement product code.

## Common Rationalizations
| Temptation | Required response |
|---|---|
| Start fresh to be thorough. | Reuse verified context and investigate only material gaps. |
| The old design says so. | Establish active authority and disclose supersession. |
| Approval proves completeness. | Preserve approval while checking evidence and acceptance gaps. |

## Red Flags
Repeated resolved questions, a competing architecture, a second implementation plan, unsupported readiness claims, or advancement beyond the current approval stage indicate a boundary violation.

## Verification
Return a concise verdict: supported within reviewed scope, material gaps, or blocked by conflicting authority. For each actionable gap, give the evidence or missing evidence, affected behavior, required correction or decision, and acceptance consequence. State review limits and remaining uncertainty. Do not recreate the full plan or treat unexecuted checks as passed.
