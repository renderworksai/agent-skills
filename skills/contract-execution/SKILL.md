---
name: contract-execution
description: Executes an already-approved engineering contract within its explicit authority and task boundary. Use when Codex receives approved scope, implementation tasks, protected behavior, and required verification commands, including preserving original failures and reporting measured completion. Excludes requirements discovery, architectural design, and work without an approved contract.
---

# Contract Execution

## Overview
Execute an approved engineering contract faithfully and stop at its boundary. The contract and applicable repository policy provide project-specific invariants, verification requirements, environment authority, and failure-triage rules. This skill grants no additional permissions.

## When to Use
Use when the user has approved concrete implementation tasks, scope, constraints, and acceptance checks. Confirm the current approval stage and active contract revision. Exclude brainstorming, architecture selection, plan authoring, and requests lacking an approved execution contract. Report missing authority rather than creating a substitute plan.

## Process
1. Read the approved contract and applicable AGENTS.md, Harness, and repository policy. Establish protected paths, successful behavior, allowed changes, dependencies, verification commands, task boundary, and stop conditions. Preserve prior verified findings with their provenance. Report material conflicts or missing prerequisites before dependent work.
2. Verify actual environment authority: working directory, repository/worktree, branch, HEAD, remotes, permissions, and uncommitted changes. Inspect ownership and authentication before authorized remote operations. Preserve unrelated user changes. Never infer Git or global environment authority from a directory name.
3. Inspect relevant implementation, callers, interfaces, and tests. Implement only approved functionality. Apply TDD where behavior changes require it: run a meaningful reproduction before the fix, preserve the observed failure, make the smallest scoped change, and rerun the same assertion. Reuse an adequate existing failing test rather than adding a duplicate.
4. Preserve protected source, inputs, invariants, and previously successful behavior. Do not weaken tests or assertions, invent numerical tolerances, introduce unapproved dependencies, or change global environments without authority. Do not invoke Superpowers, generate a second implementation plan, redesign approved architecture, or expand product scope.
5. Execute the contract's required verification from the actual working directory. Record commands, exits, and relevant output. Diagnose failures using observed root-cause evidence; retain original failures separately from later results. Perform only permitted task-local repair and related regression checks. Follow the repository's actual recovery policy and contract limits; do not impose a generic task-global retry cap. Stop and report when repair exceeds authority or the applicable stop condition is reached.

## Common Rationalizations
| Temptation | Required response |
|---|---|
| Replan first for confidence. | Inspect necessary evidence and execute approved tasks. |
| Relax the assertion to finish. | Preserve acceptance criteria and diagnose the cause. |
| The command probably passed. | Report only observed execution and exit status. |

## Red Flags
Unapproved file changes, overwritten failure evidence, unsupported PASS claims, environment changes without authority, or starting a queued feature violate the contract.

## Verification
Report completion or the exact blocker with actual commands, working directories, exits, changed paths, current HEAD, preserved original failures, final results, and unexecuted checks. Separate measured results from inference. Perform commits or remote delivery only when authorized. Stop after the approved task; never start the next product feature automatically.
