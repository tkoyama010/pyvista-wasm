# Terraform-managed repository settings

This project declares the GitHub repository settings for
`tkoyama010/pyvista-wasm` (description, merge methods, labels, Actions
permissions, Environments, etc.) using the
[`integrations/github`](https://registry.terraform.io/providers/integrations/github/latest/docs)
provider, and keeps them in sync with GitHub through the CI workflow at
[`.github/workflows/terraform.yml`](../.github/workflows/terraform.yml).

The sync workflow is the one decided in
[ADR-0009](../docs/decisions/0009-decide-how-to-sync-github-repo-settings-with-terraform.md):
CI `plan` on every PR touching `terraform/**`, CI `apply` on merge to `main`
gated by a GitHub Environment `required_reviewers` approval gate, and a
scheduled `plan -detailed-exitcode` drift check. See the issue that motivated
this work: <https://github.com/tkoyama010/pyvista-wasm/issues/531>.

## Workflow at a glance

```
PR touching terraform/**  ->  plan job posts plan as a PR comment
merge to main             ->  apply job (gated by terraform-apply env)
                                 ->  commits terraform.tfstate on success
weekly (Mon 03:17 UTC)    ->  drift job runs plan -detailed-exitcode
                                 ->  opens/updates an issue on exit code 2
```

## Authentication

### Plan job (read-only)

The `plan` job uses the auto-injected `GITHUB_TOKEN` (read scope) to run
`terraform plan`. That token is ephemeral — it lives for one job — and is not
a stored secret. It is sufficient because `plan` only reads repository
settings.

### Apply job (mutating)

ADR-0009 specifies: *the apply step uses an OIDC-minted short-lived token; no
PAT or long-lived token is stored as a repository secret for the apply step.*

The `integrations/github` provider authenticates to the GitHub REST API with a
**token**, not with an OIDC-federation flow (unlike, say, an AWS provider that
exchanges an OIDC JWT for STS credentials). GitHub does not expose an
"OIDC-to-REST-app-token" exchange that the provider could call directly.
Therefore the apply job cannot be pure-OIDC in the sense of *no token material
at all*; it must hold a token at runtime. The ADR's intent — **no long-lived
PAT, least privilege, auditability** — is honoured by using a **GitHub App**
whose installation token is minted on demand for one job and expires
immediately after:

- The workflow declares `permissions: id-token: write` on the apply job, so
  the job is OIDC-enabled (the GitHub Actions OIDC provider mints a JWT for
  the run, which the `actions/create-github-app-token` action could verify if
  the App's trust policy is later tightened to require it).
- `actions/create-github-app-token` exchanges the App credentials
  (`GH_APP_ID`, `GH_APP_INSTALLATION_ID`, `GH_APP_PEM` — stored as repository
  secrets, **not** a PAT) for a short-lived **installation token** that lives
  for the duration of this job only.
- That installation token is exported to `GITHUB_TOKEN`, which the provider
  reads at runtime. The token is never written into `terraform.tfstate`.

What is **not** used:

- No **PAT**. The App credentials are scoped to a single installation of a
  single App on this repository, can be revoked by rotating the App's key, and
  do not grant any user-scoped permission. A PAT would grant whatever the
  user has, forever, until manually rotated.
- No `secrets.GITHUB_TOKEN` in the apply step. The auto-injected token's
  scope is too narrow to manage Environments; the App token is used instead.

### One-time bootstrap (manual, outside Terraform)

Before the first apply run, a maintainer with admin scope performs these
one-time steps in the GitHub UI / via `gh`:

1. Create a GitHub App (or reuse an existing one) with the repository
   permissions the provider needs:
   `Administration: write`, `Contents: write`, `Environments: write`,
   `Issues: write`, `Metadata: read`. Install it on `tkoyama010/pyvista-wasm`.
   The workflow further scopes each minted token to exactly these via the
   `permission-*` inputs on `actions/create-github-app-token` (zizmor-clean).
1. Store the App's `app_id`, `installation_id`, and `private_key` (PEM) as
   repository secrets `GH_APP_ID`, `GH_APP_INSTALLATION_ID`, `GH_APP_PEM`.
1. Create the `terraform-apply` Environment in the repository settings:
   - `Required reviewers`: `tkoyama010`
   - `Deployment branches`: `Selected branches` -> `main` only
   - `Wait timer`: `60s` (optional cooling-off)

The Environment and its approval gate are also declared in `main.tf`
(`github_repository_environment.terraform_apply` +
`github_repository_environment_deployment_policy.main_only`), so once the
first apply imports them, drift detection catches accidental deletion. The
`required_reviewers` rule itself is set in the UI on first bootstrap; the
provider's `reviewers` block keeps it in sync thereafter.

## State

`terraform/terraform.tfstate` is **committed to the repository** (it is the
only `*.tfstate` file `.gitignore` allows). The apply job commits it back to
`main` on every successful apply, so Git history shows state evolving
alongside `main.tf`.

The state file contains no secrets: the provider reads `GITHUB_TOKEN` from
the environment at runtime and never writes it into state. Every PR that
touches `terraform/**` still shows the state diff in review, so any sensitive
field leaking into state would be caught.

State locking is not used (local backend). A single-maintainer repo with an
Environment `required_reviewers` gate serialises applies; if the maintainer
team grows, upgrade to a remote backend with locking (see ADR-0009's upgrade
path).

## Drift reconciliation

The weekly `drift` job runs `terraform plan -detailed-exitcode`. Exit code `2`
means the live GitHub settings have diverged from `terraform/` (someone
changed something in the UI). The job opens (or comments on) a GitHub issue
titled **Terraform drift detected** with the plan diff.

Reconcile by either:

1. **Revert** the manual GitHub UI change so the live state matches
   `terraform/` again, or
1. **Import** the manual change into Terraform by editing `terraform/main.tf`
   to declare the resource/setting, then open a PR. The normal plan +
   Environment-gated apply flow commits the updated state.

## Running Terraform locally

```sh
cd terraform
export GITHUB_TOKEN="$(gh auth token)"   # needs admin scope for plan/apply
terraform init
terraform plan
terraform apply    # only in CI, via the Environment-gated apply job
```

`terraform validate` and `terraform fmt -check` run in CI on every PR.
