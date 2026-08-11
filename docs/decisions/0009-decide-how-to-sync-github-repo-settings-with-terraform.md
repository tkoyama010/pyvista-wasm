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
- **Auditability**: Every `apply` must leave an immutable record of who approved it, when, against which commit, and with which plan. A maintainer running `terraform apply` on a laptop leaves no such record; only the resulting state commit exists, and nothing ties that commit to the plan the maintainer believed they were applying.
- **Drift detection**: Manual changes made through the GitHub UI must be detectable so they can be reconciled (reverted or imported) before they silently diverge from the declared state.
- **Zero-cost / GitHub-native tooling**: The project is open-source and community-driven; the sync workflow must not require paid services (e.g., Terraform Cloud paid tier, an external state backend with hosting costs) beyond GitHub Actions and the repository itself.
- **Maintainer ergonomics**: A single maintainer must be able to run the workflow end-to-end without a platform team or external coordinator.
- **State durability and recoverability**: Terraform state must survive CI runner termination and be restorable after state corruption or accidental deletion.

## Considered Options

- **CI `plan` on PR + CI `apply` on merge with OIDC and a GitHub Environment `required_reviewers` approval gate, state in repo (committed `terraform.tfstate`)**
- **CI `plan` on PR + local `apply` by maintainer, state in repo (committed `terraform.tfstate`)**
- **CI `plan` on PR + CI `apply` on merge with OIDC, state in GitHub Actions artifact**
- **CI `plan` on PR + CI `apply` on merge with stored PAT, state in a remote backend (S3/GCS/Terraform Cloud)**
- **Scheduled `plan`-only drift check in CI + local `apply`, state in repo**
- **Terraform Cloud / HCP Terraform managed workspace (plan + apply hosted)**

## Decision Outcome

Chosen option: "CI `plan` on PR + CI `apply` on merge with OIDC and a GitHub Environment `required_reviewers` approval gate, state in repo (committed `terraform.tfstate`)", because it is the only option that satisfies every knock-out driver *and* the auditability driver simultaneously: `terraform plan` runs on every PR that touches `terraform/**` so changes are reviewable; `terraform apply` runs in CI on merge but is gated by a GitHub Environment with `required_reviewers: [tkoyama010]`, so a human still approves every apply with one click — the same gesture as running `terraform apply` locally, but recorded; authentication uses OIDC, so the `integrations/github` provider receives a short-lived token minted on demand by GitHub Actions with no long-lived PAT to steal, leak, or forget to revoke; the apply job runs against the merged `main` HEAD, eliminating the stale-state footgun where a maintainer forgets `git pull` between plan and apply; state is committed to the repository as `terraform.tfstate` (by the apply job itself, on success) so it stays versioned, bisectable, and recoverable from Git history without an external backend or paid service; the GitHub Actions run history gives an immutable audit trail (actor, timestamp, commit SHA, OIDC claims, plan output) that a local apply cannot provide. The state file contains no secrets (the `integrations/github` provider reads the token from the `GITHUB_TOKEN` environment variable at runtime, never writes it into state), so committing it is safe.

### Consequences

- Good, because every settings change is reviewable in a PR — `terraform plan` output is posted to the PR by CI, so reviewers see the exact diff before merge.
- Good, because every apply is approved through a GitHub Environment `required_reviewers` gate — a human is in the loop at apply time, and the approval is recorded in the Actions run history with actor, timestamp, and commit SHA.
- Good, because no long-lived CI secret is required: OIDC mints a short-lived token on demand, scoped by an OIDC trust policy to this repository's `main` branch and this Environment. There is no PAT to revoke, no PAT to leak via shell history, `~/.terraform.d`, or a stolen laptop.
- Good, because apply runs in CI against the merged `main` HEAD — the plan the maintainer approves and the state the apply produces are always for the same commit, eliminating the local-apply footgun where a maintainer plans against one HEAD, another PR merges, and the apply silently produces a different result.
- Good, because state committed to the repo (by the apply job, on success) is bisectable with the rest of the configuration — a bad apply can be rolled back by checking out the previous `terraform.tfstate` and re-running `terraform apply`.
- Good, because drift detection is free: a scheduled `terraform plan` job (see [ADR-0005](0005-verify-agents-md-quality-in-ci.md) for the same scheduled-CI pattern) posts a failing plan when the live GitHub settings diverge from the committed state, prompting a maintainer to either import the manual change or revert it.
- Good, because it is zero-cost and GitHub-native: GitHub Actions, Environments, OIDC, and `required_reviewers` are free for public repositories, and state in Git needs no external backend.
- Good, because a single maintainer can run the whole workflow without a platform team — the only manual step is the Environment approval click, which is the same effort as running `terraform apply` locally.
- Good, because the audit trail is immutable: every apply run records who approved, when, against which commit, and with which plan output, in the GitHub Actions run history. A local apply leaves no such record.
- Bad, because it requires a one-time GitHub Actions OIDC trust configuration at the repository (or org) level — a `permissions: id-token: write` step in the workflow, an OIDC trust policy on the GitHub App or `hashicorp/tf-action-setup` side, and an Environment with `required_reviewers` set. This is a 1–2 hour setup investment that the local-apply option avoids.
- Bad, because committing `terraform.tfstate` to Git scales poorly if the state grows large or contains frequently-changing resources; for this repo's small settings surface (branches, labels, protection rules) the state file stays small and the trade-off is acceptable.
- Bad, because concurrent applies can conflict if two maintainers approve two apply runs at once; the Environment `required_reviewers` gate serialises approvals but does not lock state. For a single-maintainer repo this is negligible, but it would need a state lock (e.g., a remote backend with DynamoDB locking) if the maintainer team grows.
- Neutral, because `terraform.tfstate` must be `.gitignore`-excluded for any *unmanaged* Terraform scratch state but explicitly *tracked* for this project — a small config discipline.

### Confirmation

Compliance with this decision will be confirmed by:

1. A `terraform/` project exists in the repository with `main.tf` declaring the GitHub repository settings via the `integrations/github` provider.
1. A GitHub Actions workflow runs `terraform fmt -check`, `terraform validate`, and `terraform plan` on every PR touching `terraform/**`, and posts the plan output as a PR comment.
1. A GitHub Environment named `terraform-apply` exists with `required_reviewers: [tkoyama010]` and a `deployment_branch_policy` restricting applies to `main`.
1. The apply job in the workflow uses `permissions: id-token: write` and obtains the GitHub token via OIDC (no `secrets.GITHUB_TOKEN` or PAT is read in the apply step).
1. `terraform.tfstate` is committed to the repository by the apply job on successful apply (not `.gitignore`-d for the `terraform/` project), and Git history shows it evolving alongside `main.tf`.
1. No PAT or long-lived token is stored as a repository secret used by the `apply` step — the apply step is OIDC-only.
1. A scheduled (e.g., weekly) GitHub Actions workflow runs `terraform plan -detailed-exitcode` and opens or updates an issue when exit code indicates drift (non-zero on diff).
1. The Terraform configuration and workflow are documented in a `terraform/README.md` explaining the OIDC trust policy, the Environment approval gate, and how to reconcile drift.
1. The `integrations/github` provider is pinned to a specific version in `main.tf`, and `terraform.lock.hcl` is committed.

## Pros and Cons of the Options

### CI `plan` on PR + CI `apply` on merge with OIDC and a GitHub Environment `required_reviewers` approval gate, state in repo (committed `terraform.tfstate`)

- Good, because every settings change is reviewable in a PR via CI `plan` output.
- Good, because the Environment `required_reviewers` gate keeps a human in the loop at apply time — a merged PR does *not* apply until the maintainer clicks approve, contradicting the "no human in the loop" risk that applies only to naive OIDC apply without an Environment.
- Good, because OIDC issues short-lived tokens on demand with no long-lived secret, satisfying the no-long-lived-secrets knock-out criterion and eliminating PAT-leak vectors (shell history, `~/.terraform.d`, stolen laptop).
- Good, because apply runs in CI against the merged `main` HEAD, so the approved plan and the applied state always match the same commit — no stale-state footgun.
- Good, because the GitHub Actions run history is an immutable audit trail: every apply records the approving actor, timestamp, commit SHA, OIDC claims, and plan output.
- Good, because state in Git is bisectable and recoverable from history with no external backend, satisfying state durability at zero cost.
- Good, because drift detection is a free scheduled `plan` job.
- Good, because a single maintainer can run it end-to-end — the only manual step is the Environment approval click.
- Good, because it is zero-cost: GitHub Actions, Environments, OIDC, and `required_reviewers` are free for public repositories.
- Neutral, because it requires a one-time OIDC trust configuration (`permissions: id-token: write`, an OIDC trust policy, and an Environment with `required_reviewers`) — a 1–2 hour setup investment.
- Neutral, because `terraform.tfstate` must be explicitly tracked for this project while remaining ignored elsewhere — a small config discipline.
- Bad, because it does not scale to large state or many concurrent maintainers (no state locking); the Environment gate serialises approvals but does not lock state.

### CI `plan` on PR + local `apply` by maintainer, state in repo (committed `terraform.tfstate`)

- Good, because every settings change is reviewable in a PR via CI `plan` output.
- Good, because no long-lived CI secret is needed — `apply` runs locally with a short-lived maintainer PAT, satisfying the no-long-lived-secrets knock-out criterion *in CI*.
- Good, because state in Git is bisectable and recoverable from history with no external backend.
- Good, because drift detection is a free scheduled `plan` job.
- Good, because a single maintainer can run it end-to-end.
- Neutral, because `terraform.tfstate` must be explicitly tracked for this project while remaining ignored elsewhere — a small config discipline.
- Bad, because `apply` is manual; a merged PR can be forgotten and never applied, and drift accumulates until the next apply.
- Bad, because the short-lived PAT leaks through shell history, environment variables, and `~/.terraform.d` on the maintainer's laptop; a stolen laptop during the PAT's validity window compromises the token. OIDC has no token to steal.
- Bad, because a maintainer can plan against one HEAD, pull (or forget to pull) new merges, and apply a state that does not match any reviewed plan — the stale-state footgun. CI apply against merged `main` eliminates this.
- Bad, because there is no immutable audit trail: only the resulting `terraform.tfstate` commit exists, and nothing records which plan the maintainer believed they were applying, or from which machine.
- Bad, because it does not scale to large state or many concurrent maintainers (no state locking).

### CI `plan` on PR + CI `apply` on merge with OIDC, state in GitHub Actions artifact

See [GitHub Actions OIDC for Terraform Cloud / HCP Terraform](https://developer.hashicorp.com/terraform/tutorials/github/github-actions) and [GitHub Actions: OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect).

- Good, because `apply` is automated on merge and uses OIDC, so no long-lived secret is required.
- Good, because OIDC issues short-lived tokens with no long-lived secret, satisfying least-privilege.
- Good, because state is stored as a GitHub Actions artifact, keeping it out of Git.
- Neutral, because GitHub Actions artifacts expire (default 90 days); state must be re-uploaded each run or the artifact retention must be raised, adding config.
- Bad, because *without* a GitHub Environment `required_reviewers` gate a merged PR applies immediately with no human in the loop at apply time, increasing blast radius. This is the option the chosen option replaces — adding the Environment gate turns this "Bad" into the chosen option's "Good".
- Bad, because GitHub Actions OIDC for the `integrations/github` provider requires a GitHub App or `hashicorp/tf-action-setup` with OIDC trust configured at the GitHub org/repo level — the same one-time setup the chosen option accepts.
- Bad, because state in an artifact is not bisectable with the configuration and is lost if the workflow stops running before re-upload, failing the state-durability driver for a low-activity repo.

### CI `plan` on PR + CI `apply` on merge with stored PAT, state in a remote backend (S3/GCS/Terraform Cloud)

See [Terraform remote backends](https://developer.hashicorp.com/terraform/language/settings/backends).

- Good, because a remote backend (S3+DynamoDB, GCS, HCP Terraform) provides state locking, solving the concurrent-apply problem.
- Good, because `apply` is automated on merge.
- Good, because state is durable and not lost with CI runner termination.
- Bad, because it requires a long-lived PAT stored as a repository secret for the `apply` step, violating the no-long-lived-secrets knock-out criterion.
- Bad, because an S3/GCS backend requires a cloud account with hosting costs, violating the zero-cost driver. HCP Terraform's free tier has limits that may not cover a public repo with many settings resources.
- Bad, because it introduces external infrastructure (a cloud bucket, an HCP Terraform workspace) outside the repo, increasing the moving surface for a single-maintainer open-source project.

### Scheduled `plan`-only drift check in CI + local `apply`, state in repo

- Good, because it is identical to the local-apply option for `apply` and state, and adds only a scheduled `plan` job — which the chosen option already includes as a drift detector.
- Neutral, because this is a strict subset of the local-apply option rather than a true alternative; it is folded into the decision outcome as the drift-detection mechanism.
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

```{mermaid}
sequenceDiagram
    autonumber
    participant A as Actor
    participant PR as Pull Request
    participant CI as GitHub Actions
    participant ENV as Environment<br/>required_reviewers
    participant GH as GitHub API
    participant GIT as Git (repo)

    A->>PR: Open PR touching terraform/**
    PR->>CI: Trigger plan workflow
    CI->>GH: terraform fmt -check / validate
    CI->>GH: terraform plan (read-only GITHUB_TOKEN)
    CI->>PR: Post plan output as comment
    A->>PR: Review plan, merge PR
    PR->>CI: Trigger apply workflow on merge
    CI->>ENV: Request apply approval
    Note over ENV,A: Apply job pauses —<br/>no token minted yet
    A->>ENV: Click Approve in Actions UI
    ENV->>CI: Approval recorded (actor, timestamp)
    CI->>GH: Mint OIDC short-lived token
    CI->>GH: terraform apply (scoped to main + terraform-apply)
    GH-->>CI: Apply result
    CI->>GIT: Commit terraform.tfstate on success
    CI->>PR: Post apply result

    Note over CI,GH: Weekly scheduled drift check
    CI->>GH: terraform plan -detailed-exitcode
    GH-->>CI: Exit code 2 = drift detected
    CI->>PR: Open or update drift issue
```

### Why the Environment approval gate changes the OIDC calculus

A naive "CI apply on merge with OIDC" workflow applies a merged PR immediately with no human in the loop — the blast-radius objection that pushed the first draft of this ADR toward local apply. A GitHub Environment with `required_reviewers: [tkoyama010]` removes that objection: the apply job does not start until the maintainer clicks *Approve* in the Actions UI, the approval is recorded in the run history with actor and timestamp, and the maintainer can inspect the plan output attached to the run before approving. The effort is one click — the same as typing `terraform apply` on a laptop — but the safety properties are strictly better: no PAT on the maintainer's machine, no stale-state footgun, and an immutable audit trail. The Environment can also add a `wait_timer` (cooling-off period after approval) and a `deployment_branch_policy` restricting applies to `main`.

### Drift reconciliation

When the scheduled `terraform plan -detailed-exitcode` reports a diff (exit code 2), the workflow opens (or updates) a GitHub issue listing the drift. A maintainer then either:

1. reverts the manual GitHub UI change so the live state matches the committed configuration, or
1. imports the manual change into Terraform by editing `main.tf` to declare the resource/setting and opening a PR; the normal PR `plan` + Environment-gated `apply` flow commits the updated state.

### Token scope and safety

- The CI `plan` step uses the default `GITHUB_TOKEN` (read-only) or an OIDC-minted short-lived token, with the minimum scope needed to read repository settings.
- The CI `apply` step uses an OIDC-minted short-lived token. The OIDC trust policy restricts the token to this repository's `main` branch and the `terraform-apply` Environment, so a token minted for any other repo, branch, or Environment cannot be used to apply.
- No PAT is ever stored on a maintainer's laptop, in a repository secret, or in shell history. The `integrations/github` provider reads the token from the `GITHUB_TOKEN` environment variable at runtime; it is never written into `terraform.tfstate`. The state file is therefore safe to commit, but is reviewed in PRs like any other change to confirm no sensitive field leaks.

### Upgrade path

If the maintainer team grows beyond one or state locking becomes necessary, upgrade to a remote backend with locking (e.g., S3+DynamoDB or HCP Terraform) while keeping the OIDC + Environment approval gate. The committed `terraform.tfstate` can be imported into the remote backend with `terraform state pull` / `terraform state push`, so the chosen option does not lock the project out of upgrading. If OIDC trust configuration proves too burdensome, the team can fall back to the local-apply option — but this trades auditability and the stale-state safety net for setup convenience, and is not recommended for any repo where a bad apply can lock maintainers out.

### Links

- `integrations/github` provider: [https://registry.terraform.io/providers/integrations/github/latest/docs](https://registry.terraform.io/providers/integrations/github/latest/docs)
- GitHub Actions OIDC: [https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- GitHub Environments: [https://docs.github.com/en/actions/deployment/targeting-deployments/environments](https://docs.github.com/en/actions/deployment/targeting-deployments/environments)
- HCP Terraform: [https://developer.hashicorp.com/terraform/cloud-docs](https://developer.hashicorp.com/terraform/cloud-docs)
- Parent story: [#513](https://github.com/tkoyama010/pyvista-wasm/issues/513) (Manage and sync GitHub repository settings with Terraform)
- This decision: [#514](https://github.com/tkoyama010/pyvista-wasm/issues/514)
- Related: [ADR-0005](0005-verify-agents-md-quality-in-ci.md) (scheduled-CI verification pattern reused for drift detection)
