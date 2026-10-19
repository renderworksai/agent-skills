# Engineering Skills V1

This fork adds two independent, instruction-only skills to upstream
`addyosmani/agent-skills` at `aeac41d4d005999432bb7312f7ff06383a91d59d`
(plugin version `0.6.13`). The original 25 skills, evaluation algorithms, and
MIT license remain unchanged. New contributions are also MIT licensed.

- `skills/planning-integrity/SKILL.md` checks evidence and completeness of an
  existing plan. Superpowers retains design, planning, and approval ownership.
- `skills/contract-execution/SKILL.md` executes an already-approved contract
  under its actual repository policy and stops at the authorized task boundary.

The existing planning skill authors a task plan and incremental implementation
delivers slices. These additions preserve an existing approved plan and its
execution authority; they introduce no new router, server, or orchestration.
Catalog, rejection-ledger, and open-proposal preflight inspection found no
identical approved-contract or existing-plan-integrity skill at this baseline.
No upstream pull request, merge, or public release is part of this delivery.

## Validation evidence

Commands run from the fork root:

```sh
node scripts/validate-skills.js
node scripts/validate-reference-links.js
node scripts/run-evals.js --min-rank1 95
git diff --check
node --test scripts/lib/skill-lint-test.js scripts/run-evals-test.js scripts/validate-reference-links-test.js
```

Baseline: all four required commands exited 0; routing was 91/91 (100%).
After adding cases, before skills: routing runner exited 1 solely for two
missing skill directories; this is structural RED, not behavioral failure.
After skills: required validators exited 0; 27 skills, no errors or warnings;
routing was 97/97 (100%), with 155 checks passed. Relevant validator regression
tests: 160 passed. No thresholds, prompts, or upstream algorithms were weakened.

The two planning behavioral cases use `kind: dialogue` because a focused review
is their conversational deliverable; their complete synthetic evidence is
embedded in the prompt. The two execution cases use a real synthetic repository
fixture. The fixture deliberately has a CRLF regression and must remain broken
until an actual executor repairs its disposable copy. Its tests are not part of
the fork's passing test suite. Do not fix or exclude that fixture to fake GREEN.

Actual agent behavioral execution remains **UNVERIFIED**: no extra agent or paid
case was run. The optional skill-creator Python validator was unavailable due
to missing PyYAML; no dependency was installed. Required upstream validators
and strict parsing with existing Ruby `YAML.safe_load` were used instead.

## Reproduce the private skills-only package

Use a fresh output directory outside this repository:

```sh
mkdir -p "$ENGINEERING_SKILLS_OUT"
curl --fail --location https://agent-plugins.org/schemas/1.0.0/plugin.schema.json \
  --output "$ENGINEERING_SKILLS_OUT/plugin.schema.json"
python3 scripts/package-engineering-skills.py \
  --out "$ENGINEERING_SKILLS_OUT" \
  --schema "$ENGINEERING_SKILLS_OUT/plugin.schema.json"
ENGINEERING_PLUGIN_SCHEMA="$ENGINEERING_SKILLS_OUT/plugin.schema.json" \
  PYTHONDONTWRITEBYTECODE=1 python3 scripts/package-engineering-skills-test.py
```

Set `ENGINEERING_SKILLS_OUT` to the desired fresh absolute output directory
before running these commands. Python 3 and Ruby with standard JSON/YAML are
required; no third-party packages are used. The builder checks the complete
assertion vocabulary in the downloaded canonical schema and fails on unknown
keywords; it is not a general JSON Schema engine. OpenAI interface semantics
and the 30-character subtitle limit are checked separately. The four-member
ZIP is deterministic and is reopened for byte, UTF-8/YAML, attribution,
allowlist, path, file-type, and secret-signature checks. Eight safety tests
include malicious paths, symlinks, extra/duplicate members, and modified bytes.

The output contains only Planning Integrity. Account-side ChatGPT import and
actual Web invocation remain user actions. Use the private plugin import flow
available to the account; if ZIP import is unavailable, report that interface
limitation rather than inventing a menu or configuring an MCP server.

## Install the same pinned Contract Execution skill elsewhere

Use the full verified source commit and skill SHA-256 from the delivery report.
Fetch that exact commit from this fork into a new temporary checkout, extract
only `skills/contract-execution/SKILL.md`, verify its SHA-256, and install a copy
under `$HOME/.agents/skills/contract-execution/SKILL.md`. Check destination
ownership and retain a recoverable old version before any controlled update.
Never symlink to the development branch. Do not copy the repository AGENTS.md,
the always-on router, or the other upstream skills into the global directory.
This recipe applies to another Mac or Jetson; neither is modified by this goal.

Local installation byte checks and native discovery receipts are in the final
delivery report. Native discovery does not prove behavioral adherence. No
global Codex configuration, model, reasoning effort, dependency, or runtime
setting changes are required.
