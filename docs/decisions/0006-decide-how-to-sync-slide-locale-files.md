---
status: accepted
date: 2026-08-07
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Decide how to keep slide locale files in sync (JA/EN)

## Context and Problem Statement

[ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) decided to internationalize the Slidev deck using `slidev-addon-i18nb` with separate YAML locale files: `slides/locales/ja.yml` (Japanese, authoritative) and `slides/locales/en.yml` (English). A consequence of storing translations in separate files is that the two locales can be maintained independently — and therefore can also drift independently. Issue [#441](https://github.com/tkoyama010/pyvista-wasm/issues/441) surfaced that drift has already occurred: `en.yml` carries 3 stale top-level sections (`caps`, `perf`, `constraints`) for slides that no longer exist in the authoritative `ja.yml`, shared sections have diverged in content (JA titles are longer and more descriptive while EN titles are shorter and less current), and the `speaker_title` / `speaker_subtitle` key assignments are swapped in the `agenda` section. ADR-0003 decided *how* to internationalize the deck but did not decide *how to keep the two locale files in sync* over time. Without a documented policy, drift will recur every time one language is updated without touching the other. How should we keep the two locale files in sync?

## Decision Drivers

- **JA is authoritative**: Japanese is the newest, most-refined content — the deck is authored in JA first and translated to EN. The sync policy must treat JA as the source of truth for slide structure.
- **Structural drift detection**: The policy must detect when one locale has sections or keys that the other lacks — the exact drift that produced the 3 stale sections in `en.yml`. This is a knock-out criterion.
- **Content drift detection**: The policy should help detect when one language's content has been updated but the other's has not — e.g., a JA title rewritten while the EN title stays stale.
- **CI enforcement vs. manual review**: Automated enforcement catches drift without relying on a reviewer remembering to compare two files; manual review alone has already failed (the drift in [#441](https://github.com/tkoyama010/pyvista-wasm/issues/441) went unnoticed).
- **Zero-cost / GitHub-native tooling**: Per [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) drivers, the solution must not require paid services, external API keys, or accounts beyond what is already in the repository.
- **Minimal maintenance burden**: This is a single-maintainer open-source project; the sync policy must be cheap to set up and require near-zero ongoing effort.

## Considered Options

- **JA-authoritative with CI key-parity check** — a pre-commit hook or CI script that recursively compares the key structure of `ja.yml` and `en.yml` and fails if they differ; JA is the structural source of truth
- **JA-authoritative with CI key-parity + untranslated-value check** — key-parity check plus a check that flags EN values still matching JA values (or containing Japanese characters), indicating untranslated content
- **Dual-maintenance with no enforcement** — status quo; rely on PR review to catch drift
- **Single-source-of-truth with build-time translation** — one locale (JA) is the source; the EN file is generated from it, either by AI-assisted translation or a manual template process
- **PR-template co-modification checklist** — add a checkbox to the PR template requiring the author to confirm both locale files were updated; process-only, no automation

## Decision Outcome

Chosen option: **"JA-authoritative with CI key-parity check"**, because it is the minimal automated guard that catches the structural drift that already occurred (3 stale sections in `en.yml`), integrates with the project's existing pre-commit / pre-commit.ci infrastructure (zero-cost, GitHub-native, no external services), and requires negligible ongoing maintenance from a single maintainer. Content drift (stale or swapped translations) is left to manual PR review because automated detection would either require AI/LLM services — violating the zero-cost driver — or produce unacceptable false-positive rates from legitimately shared values (e.g., "PyVista on WebAssembly", "PyCon JP 2026", code labels).

### Consequences

- Good, because structural drift between `ja.yml` and `en.yml` is caught automatically — a PR that adds a section to `ja.yml` without updating `en.yml` (or vice versa) fails the key-parity check.
- Good, because the check runs through the existing pre-commit infrastructure (local hook + pre-commit.ci), so no new CI workflow or external service is needed.
- Good, because JA is explicitly designated as the authoritative locale for structure, making the maintenance direction clear: update JA first, then mirror the structure in EN.
- Good, because the maintenance burden is near-zero — the check is a small script that compares key sets; it does not need updating when slides are added or removed (it compares whatever keys exist).
- Bad, because the check does not detect content drift — an EN translation can become stale (outdated wording) without triggering a failure, since only key structure is compared, not values.
- Bad, because the check does not detect swapped key assignments (as occurred in `agenda`): the keys `speaker_title` and `speaker_subtitle` exist in both files, so key parity passes even when their values are semantically swapped.
- Neutral, because the check treats JA as structurally authoritative but does not enforce translation direction; a maintainer could still update EN first and mirror to JA, though the policy recommends JA-first.

### Confirmation

Compliance with this decision will be confirmed by:

1. A local pre-commit hook (or CI script) exists that recursively compares the top-level sections and nested keys of `slides/locales/ja.yml` and `slides/locales/en.yml`, exiting non-zero if the key sets differ.
1. The hook is registered in `.pre-commit-config.yaml` and runs automatically in pre-commit.ci on every PR that touches either locale file.
1. `slides/locales/ja.yml` is documented (in the ADR and/or a comment in the locale directory) as the authoritative locale for slide structure.
1. The 3 stale sections (`caps`, `perf`, `constraints`) identified in [#441](https://github.com/tkoyama010/pyvista-wasm/issues/441) are removed from `en.yml` so that the key-parity check passes.
1. Running the hook against the current locale files succeeds (key structures match).
1. A deliberate test (adding a key to `ja.yml` without updating `en.yml`) causes the hook to fail with a clear message identifying the missing key.

## Pros and Cons of the Options

### JA-authoritative with CI key-parity check

A script — implemented as a local pre-commit hook — loads both YAML files, recursively collects every key path (e.g., `cover.title`, `agenda.i1t`), and compares the two sets. If JA has a key that EN lacks, or EN has a key that JA lacks, the hook fails and names the offending keys. JA is the authoritative source of truth for structure.

- Good, because it directly satisfies the structural-drift knock-out criterion: the 3 stale sections in `en.yml` would have been caught immediately.
- Good, because it integrates with the existing pre-commit / pre-commit.ci infrastructure already configured in `.pre-commit-config.yaml` — no new CI workflow, no external service, fully zero-cost and GitHub-native.
- Good, because it is a small script (~20 lines using `yaml.safe_load` and a recursive key walker) with no dependencies beyond PyYAML, which is already in the project.
- Good, because it requires negligible ongoing maintenance — the script compares whatever keys exist, so it never needs updating when slides are added or removed.
- Good, because it runs locally (pre-commit install) and in CI (pre-commit.ci), so drift is caught before merge.
- Neutral, because it catches structural drift but not content drift — a stale EN translation with the correct key structure passes the check.
- Bad, because it does not detect swapped key assignments (as in `agenda.speaker_title` / `speaker_subtitle`): both keys exist in both files, so parity passes despite the semantic swap.
- Bad, because it does not flag EN values that are still in Japanese (copy-pasted but never translated) — the value content is not inspected.

### JA-authoritative with CI key-parity + untranslated-value check

Everything in the key-parity check, plus an additional check that inspects EN values. Two interpretations exist: (a) flag EN values that are byte-identical to the corresponding JA values — catching content that was copied but never translated; (b) flag EN values that contain Japanese characters (Hiragana, Katakana, or Kanji) — catching definitively untranslated text.

- Good, because it catches a superset of what the key-parity check alone catches — including some content drift.
- Good, because interpretation (b) — flagging Japanese characters in EN values — is precise: Japanese text in an EN locale file is always wrong, so there are zero false positives. The check is a cheap character-range scan.
- Good, because both checks use the same pre-commit infrastructure and remain zero-cost.
- Neutral, because interpretation (a) — flagging byte-identical values — has many false positives: legitimately shared values like "PyVista on WebAssembly", "PyCon JP 2026", `js_label`, `py_label`, and `code_label` are identical in both locales by design.
- Bad, because neither interpretation detects *stale* translations — an EN value that was once translated but is now outdated (the JA text was rewritten) is not byte-identical and contains no Japanese characters, so it passes.
- Bad, because interpretation (a)'s false-positive rate would require an allowlist of legitimately shared values, adding maintenance burden for a single maintainer.
- Bad, because the incremental benefit over key-parity alone is marginal for this project: the most damaging drift (stale sections referencing non-existent slides) is already caught by key parity.

### Dual-maintenance with no enforcement — status quo

Both locale files are maintained independently. Drift is caught only if a reviewer manually compares the two files during PR review.

- Good, because it requires no tooling, no script, and no CI changes — zero setup effort.
- Good, because it imposes no constraints on how or when each locale is edited.
- Neutral, because it is the current state; no migration is needed.
- Bad, because it has already failed: the drift documented in [#441](https://github.com/tkoyama010/pyvista-wasm/issues/441) — 3 stale sections, diverged content, swapped keys — went unnoticed through existing PR review.
- Bad, because it relies on a reviewer remembering to compare two files that may be hundreds of lines apart in the diff — this is exactly the kind of check that humans skip under review pressure.
- Bad, because drift accumulates silently: each one-sided edit adds a small discrepancy, and there is no signal until someone notices a broken slide or stale text.

### Single-source-of-truth with build-time translation

One locale (JA) is the canonical source. The EN file is generated from it, either by an AI-assisted translation pipeline (e.g., an LLM API) or by a manual template process where JA is copied and translated into EN before each build.

- Good, because it eliminates structural drift by construction — the EN file is derived from JA, so it can never have sections that JA lacks.
- Good, because it enforces JA-authoritative at the deepest level: there is only one source of truth.
- Neutral, because a manual template process (copy JA, translate each value) is a disciplined workflow but provides no automation — it is a convention, not a guard.
- Bad, because AI-assisted translation requires an LLM API key (e.g., Gemini, OpenAI), violating the zero-cost / GitHub-native driver established in [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md).
- Bad, because AI-generated translations require review and correction — the output is not production-ready without human checking, so the "generation" step saves transcription effort but not review effort.
- Bad, because a build-time generation step adds complexity to the CI pipeline (a translation script, API key management, review of generated diffs) that is disproportionate for a single-maintainer talk deck.
- Bad, because a manual template process is unenforceable — nothing prevents a maintainer from editing `en.yml` directly, reintroducing the drift problem.

### PR-template co-modification checklist — manual confirmation in the PR template

A checkbox is added to `.github/pull_request_template.md` requiring the author to confirm: "If this PR touches slide content, both `slides/locales/ja.yml` and `slides/locales/en.yml` have been updated."

- Good, because it is trivially zero-cost and GitHub-native — only a PR template edit.
- Good, because it raises awareness: the author is prompted to think about both locales before opening the PR.
- Good, because it is compatible with any other option (key-parity check, untranslated-value check, etc.) as a complementary process guard.
- Neutral, because it adds a small amount of boilerplate to every PR, even those that do not touch slides.
- Bad, because it is a manual check with no enforcement — an author can tick the box without actually verifying both files, and nothing fails automatically.
- Bad, because it does not detect drift; it only prompts the author to self-audit, which is no more reliable than the status-quo PR review that already failed in [#441](https://github.com/tkoyama010/pyvista-wasm/issues/441).
- Bad, because it provides no structural or content verification — it is a reminder, not a guard.

## More Information

### Comparison matrix

The table below summarises how each option scores against the evaluation criteria. ✓ = strong, ~ = partial, ✗ = weak.

| Criterion | Key-parity check | Key-parity + value check | No enforcement (status quo) | Single-source build-time | PR-template checklist |
|---|:---:|:---:|:---:|:---:|:---:|
| Structural drift detection | ✓ | ✓ | ✗ | ✓ | ✗ |
| Content drift detection | ✗ | ~ | ✗ | ~ | ✗ |
| CI enforcement (automated) | ✓ | ✓ | ✗ | ~ | ✗ |
| Zero-cost / GitHub-native | ✓ | ✓ | ✓ | ✗ | ✓ |
| Minimal maintenance burden | ✓ | ~ | ✓ | ✗ | ✓ |
| Catches swapped key assignments | ✗ | ✗ | ✗ | ✓ | ✗ |

### Links

- Parent issue: [#441](https://github.com/tkoyama010/pyvista-wasm/issues/441) (Update English slide locale to match newest Japanese content)
- This decision: [#442](https://github.com/tkoyama010/pyvista-wasm/issues/442)
- Related: [ADR-0003](0003-decide-how-to-internationalize-the-slidev-deck.md) (established the i18n structure with separate YAML locale files)
- Related: [ADR-0004](0004-adopt-one-slide-one-message-principle.md) (governs slide content density, which affects when locale keys change)
- Related: [#439](https://github.com/tkoyama010/pyvista-wasm/issues/439) (ADR-0005 — deciding how to internationalize the ReadTheDocs documentation, not yet written)
- Existing pre-commit configuration: [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml)
