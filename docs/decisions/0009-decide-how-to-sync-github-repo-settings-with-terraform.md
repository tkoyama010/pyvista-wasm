---
status: accepted
date: 2026-08-11
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Decide how to sync GitHub repository settings with Terraform

## Context and Problem Statement

The parent story [#513](https://github.com/tkoyama010/pyvista-wasm/issues/513) ships a Terraform project that declares the GitHub repository settings for `tkoyama010/pyvista-wasm` (branches, protection rules, labels, collaborators, Actions secrets, etc.) using the `integrations/github` provider. Declaring the resources in HCL is only half the work; the other half is the *workflow* that keeps the live GitHub settings in sync with that declaration. Today the settings are configured through the GitHub UI, which is unversioned, unreviewable, and easy to drift. We need to decide how `terraform plan` and `terraform apply` are run, where Terraform state lives, how the GitHub token is supplied, how drift is reconciled, and who is allowed to apply — so that repository configuration is versioned, reviewable, reproducible, and recoverable after accidental UI changes. Which sync workflow should we adopt?

## Decision Drivers

- **Reviewability of settings changes**: Every change to repository settings must go through a PR so it is reviewable and bisectable, the same way code changes do. This is a knock-out criterion.
- **No long-lived secrets in CI**: The CI workflow must not rely on a long-lived personal access token (PAT) stored as a repository secret if a short-lived, scoped alternative exists. Least-privilege authentication is a knock-out criterion.
- **Blast-radius control**: A bad `terraform apply` can lock maintainers out of the repository, delete branches, or wipe protection rules. The workflow must make it hard to apply blindly and easy to recover.
- **Drift detection**: Manual changes made through the GitHub UI must be detectable so they can be reconciled (reverted or imported) before they silently diverge from the declared state.
- **Zero-cost / GitHub-native tooling**: The project is open-source and community-driven; the sync workflow must not require paid services (e.g., Terraform Cloud paid tier, an external state backend with hosting costs) beyond GitHub Actions and the repository itself.
- **Maintainer ergonomics**: A single maintainer must be able to run the workflow end-to-end without a platform team or external coordinator.
- **State durability and recoverability**: Terraform state must survive CI runner termination and be restorable after state corruption or accidental deletion.

## Considered Options

- **CI `plan` on PR + local `apply` by maintainer, state in repo (committed `terraform.tfstate`)**
- **CI `plan` on PR + CI `apply` on merge with OIDC, state in GitHub Actions artifact**
- **CI `plan` on PR + CI `apply` on merge with stored PAT, state in a remote backend (S3/GCS/Terraform Cloud)**
- **Scheduled `plan`-only drift check in CI + local `apply`, state in repo**
- **Terraform Cloud / HCP Terraform managed workspace (plan + apply hosted)**

## Decision Outcome

Chosen option: "CI `plan` on PR + local `apply` by maintainer, state in repo (committed `terraform.tfstate`)", because it satisfies every knock-out driver with the smallest moving surface: `terraform plan` runs on every PR that touches the Terraform project so changes are reviewable; `terraform apply` is run locally by a maintainer after merge using a short-lived PAT issued from the maintainer's own GitHub account (no long-lived CI secret, no OIDC trust config to maintain); state is committed to the repository as `terraform.tfstate` so it is versioned, bisectable, and recoverable from Git history without an external backend or paid service. The state file contains no secrets (the `integrations/github` provider reads the token from the `GITHUB_TOKEN` environment variable at runtime, never writes it into state), so committing it is safe.

### Consequences

- Good, because every settings change is reviewable in a PR — `terraform plan` output is posted to the PR by CI, so reviewers see the exact diff before merge.
- Good, because no long-lived CI secret is required: the maintainer runs `terraform apply` locally with a PAT issued on the fly from their own account, scoped to the `repo` and `admin:org` (if applicable) scopes, and revoked or allowed to expire immediately after.
- Good, because state committed to the repo is bisectable with the rest of the configuration — a bad apply can be rolled back by checking out the previous `terraform.tfstate` and re-running `terraform apply`.
- Good, because drift detection is free: a scheduled `terraform plan` job (see [ADR-0005](0005-verify-agents-md-quality-in-ci.md) for the same scheduled-CI pattern) posts a failing plan when the live GitHub settings diverge from the committed state, prompting a maintainer to either import the manual change or revert it.
- Good, because it is zero-cost and GitHub-native: GitHub Actions runs `plan` for free on public repositories, and state in Git needs no external backend.
- Good, because a single maintainer can run the whole workflow without a platform team.
- Bad, because `terraform apply` is not automated — a maintainer must run it locally after merge, adding a manual step and a small risk that a merged PR is forgotten and never applied.
- Bad, because committing `terraform.tfstate` to Git scales poorly if the state grows large or contains frequently-changing resources; for this repo's small settings surface (branches, labels, protection rules) the state file stays small and the trade-off is acceptable.
- Bad, because concurrent applies can conflict (two maintainers running `terraform apply` at once); for a single-maintainer repo this is negligible, but it would need a state lock (e.g., a remote backend with DynamoDB locking) if the maintainer team grows.
- Neutral, because `terraform.tfstate` must be `.gitignore`-excluded for any *unmanaged* Terraform scratch state but explicitly *tracked* for this project — a small config discipline.

### Confirmation

Compliance with this decision will be confirmed by:

1. A `terraform/` project exists in the repository with `main.tf` declaring the GitHub repository settings via the `integrations/github` provider.
1. A GitHub Actions workflow runs `terraform fmt -check`, `terraform validate`, and `terraform plan` on every PR touching `terraform/**`, and posts the plan output as a PR comment.
1. `terraform.tfstate` is committed to the repository (not `.gitignore`-d for the `terraform/` project), and Git history shows it evolving alongside `main.tf`.
1. No PAT or token is stored as a repository secret used by the `apply` step — `apply` is documented as a local-only maintainer step.
1. A scheduled (e.g., weekly) GitHub Actions workflow runs `terraform plan -detailed-exitcode` and opens or updates an issue when exit code indicates drift (non-zero on diff).
1. The Terraform configuration and workflow are documented in a `terraform/README.md` explaining the local `apply` workflow, the PAT scope required, and how to reconcile drift.
1. The `integrations/github` provider is pinned to a specific version in `main.tf`, and `terraform.lock.hcl` is committed.

## Pros and Cons of the Options

### CI `plan` on PR + local `apply` by maintainer, state in repo (committed `terraform.tfstate`)

- Good, because every settings change is reviewable in a PR via CI `plan` output.
- Good, because no long-lived CI secret is needed — `apply` runs locally with a short-lived maintainer PAT, satisfying the no-long-lived-secrets knock-out criterion.
- Good, because state in Git is bisectable and recoverable from history with no external backend, satisfying state durability at zero cost.
- Good, because drift detection is a free scheduled `plan` job.
- Good, because a single maintainer can run it end-to-end.
- Neutral, because `terraform.tfstate` must be explicitly tracked for this project while remaining ignored elsewhere — a small config discipline.
- Bad, because `apply` is manual; a merged PR can be forgotten and never applied.
- Bad, because it does not scale to large state or many concurrent maintainers (no state locking).

### CI `plan` on PR + CI `apply` on merge with OIDC, state in GitHub Actions artifact

See [GitHub Actions OIDC for Terraform Cloud / HCP Terraform](https://developer.hashicorp.com/terraform/tutorials/github/github-actions) and [GitHub Actions: OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect).

- Good, because `apply` is automated on merge — no manual maintainer step, no forgotten PRs.
- Good, because OIDC issues short-lived tokens with no long-lived secret, satisfying least-privilege.
- Good, because state is stored as a GitHub Actions artifact, keeping it out of Git.
- Neutral, because GitHub Actions artifacts expire (default 90 days); state must be re-uploaded each run or the artifact retention must be raised, adding config.
- Bad, because GitHub Actions OIDC for the `integrations/github` provider requires a GitHub App or `hashicorp/tf-action-setup` with OIDC trust configured at the GitHub org/repo level — non-trivial setup for a single-maintainer open-source repo.
- Bad, because state in an artifact is not bisectable with the configuration and is lost if the workflow stops running before re-upload, failing the state-durability driver for a low-activity repo.
- Bad, because automated `apply` on merge increases blast radius: a merged PR applies immediately with no human in the loop at apply time.

### CI `plan` on PR + CI `apply` on merge with stored PAT, state in a remote backend (S3/GCS/Terraform Cloud)

See [Terraform remote backends](https://developer.hashicorp.com/terraform/language/settings/backends).

- Good, because a remote backend (S3+DynamoDB, GCS, HCP Terraform) provides state locking, solving the concurrent-apply problem.
- Good, because `apply` is automated on merge.
- Good, because state is durable and not lost with CI runner termination.
- Bad, because it requires a long-lived PAT stored as a repository secret for the `apply` step, violating the no-long-lived-secrets knock-out criterion.
- Bad, because an S3/GCS backend requires a cloud account with hosting costs, violating the zero-cost driver. HCP Terraform's free tier has limits that may not cover a public repo with many settings resources.
- Bad, because it introduces external infrastructure (a cloud bucket, an HCP Terraform workspace) outside the repo, increasing the moving surface for a single-maintainer open-source project.

### Scheduled `plan`-only drift check in CI + local `apply`, state in repo

- Good, because it is identical to the chosen option for `apply` and state, and adds only a scheduled `plan` job — which the chosen option already includes as a drift detector.
- Neutral, because this is a strict subset of the chosen option rather than a true alternative; it is folded into the decision outcome as the drift-detection mechanism.
- Bad, because considered as a standalone option it leaves PR-time `plan` unspecified, weakening the reviewability knock-out criterion.

### Terraform Cloud / HCP Terraform managed workspace (plan + apply hosted)

See [HCP Terraform](https://developer.hashicorp.com/terraform/cloud-docs).

- Good, because it hosts both `plan` and `apply`, providing a UI for run history, state, and approvals.
- Good, because it supports OIDC and short-lived tokens, satisfying least-privilege.
- Good, because state is managed by HCP Terraform with locking and version history.
- Bad, because it introduces an external hosted service with its own access control, billing, and quota — violating the zero-cost / GitHub-native driver for a public repo.
- Bad, because it moves the apply decision out of the repository's PR flow, reducing the "everything travels through the same review/PR flow as code" property the repo values (see [ADR-0000](0000-use-markdown-architectural-decision-records.md)).
- Bad, because the free tier has a limited number of workspaces and runs per month, which may not cover sustained activity.

## More Information

### Chosen workflow at a glance

| Step | Where | Who | Token |
|---|---|---|---|
| `terraform fmt -check` / `validate` | CI on PR | GitHub Actions | none (read-only) |
| `terraform plan` | CI on PR | GitHub Actions | read-only PAT or `GITHUB_TOKEN` (provider reads only) |
| `terraform plan` (drift check) | CI scheduled (weekly) | GitHub Actions | read-only PAT |
| `terraform apply` | local, after merge | maintainer | short-lived PAT, scoped, revoked after |
| State storage | committed `terraform.tfstate` | Git | n/a |

### Drift reconciliation

When the scheduled `terraform plan -detailed-exitcode` reports a diff (exit code 2), the workflow opens (or updates) a GitHub issue listing the drift. A maintainer then either:

1. reverts the manual GitHub UI change so the live state matches the committed configuration, or
2. imports the manual change into Terraform by editing `main.tf` to declare the resource/setting and running `terraform apply` locally to commit the updated state.

### Token scope and safety

- The CI `plan` step uses a read-only PAT (or the default `GITHUB_TOKEN` if the provider supports it for the resources declared) with the minimum scope needed to read repository settings.
- The local `apply` step uses a classic or fine-grained PAT issued from the maintainer's account with `repo` scope (and `admin:org` only if org-level resources are declared), valid for the shortest lifetime GitHub allows, and revoked immediately after the apply completes.
- The `integrations/github` provider reads the token from the `GITHUB_TOKEN` environment variable at runtime; it is never written into `terraform.tfstate`. The state file is therefore safe to commit, but is reviewed in PRs like any other change to confirm no sensitive field leaks.

### Upgrade path

If the maintainer team grows beyond one or state locking becomes necessary, upgrade to a remote backend with locking (e.g., S3+DynamoDB or HCP Terraform) and move `apply` into CI with OIDC. The committed `terraform.tfstate` can be imported into the remote backend with `terraform state pull` / `terraform state push`, so the chosen option does not lock the project out of upgrading.

### Links

- `integrations/github` provider: [https://registry.terraform.io/providers/integrations/github/latest/docs](https://registry.terraform.io/providers/integrations/github/latest/docs)
- GitHub Actions OIDC: [https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- HCP Terraform: [https://developer.hashicorp.com/terraform/cloud-docs](https://developer.hashicorp.com/terraform/cloud-docs)
- Parent story: [#513](https://github.com/tkoyama010/pyvista-wasm/issues/513) (Manage and sync GitHub repository settings with Terraform)
- This decision: [#514](https://github.com/tkoyama010/pyvista-wasm/issues/514)
- Related: [ADR-0005](0005-verify-agents-md-quality-in-ci.md) (scheduled-CI verification pattern reused for drift detection)
