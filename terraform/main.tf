terraform {
  required_version = ">= 1.15.0"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.6.0"
    }
  }
}

# ponytail: token read from GITHUB_TOKEN env var (OIDC-minted in CI).
# Never written into state. See terraform/README.md.
provider "github" {
  owner = "tkoyama010"
}

locals {
  repository_name = "pyvista-wasm"
  maintainer      = "tkoyama010"
}

data "github_user" "maintainer" {
  username = local.maintainer
}

resource "github_repository" "this" {
  name                   = local.repository_name
  description            = "PyVista-like API for VTK.wasm — bring intuitive 3D visualization to the browser using WebAssembly."
  homepage_url           = "https://pyvista-wasm.readthedocs.io/en/latest/"
  visibility             = "public"
  has_issues             = true
  has_projects           = true
  has_wiki               = true
  has_discussions        = true
  delete_branch_on_merge = true

  # Merge methods: squash only.
  allow_squash_merge = true
  allow_merge_commit = false
  allow_rebase_merge = false

  squash_merge_commit_title = "PR_TITLE"
  merge_commit_title        = "MERGE_MESSAGE"

  # Allow auto-merge so dependabot/renovate PRs can auto-merge on green.
  allow_auto_merge = true

  # Preserve existing settings captured on import (do not let them drift to
  # provider defaults on the next apply).
  allow_update_branch         = true
  vulnerability_alerts        = true
  web_commit_signoff_required = false

  # The auto GITHUB_TOKEN used by the read-only plan/drift jobs cannot read
  # the vulnerability-alerts endpoint (403). Skip that read so plan works
  # with least-privilege tokens; the apply job (App token, Administration:
  # write) still reconciles this field.
  ignore_vulnerability_alerts_during_read = true

  # Squash commits carry only the PR title, no body list.
  squash_merge_commit_message = "BLANK"

  # ponytail: auto_init false — repo already exists. GitHub Pages is served
  # from gh-pages; the provider manages the source here so it does not drift.
  auto_init = false

  pages {
    source {
      branch = "gh-pages"
      path   = "/"
    }
  }
}

resource "github_branch_default" "this" {
  repository = github_repository.this.name
  branch     = "main"
}

# ponytail: Actions permissions (allowed actions, workflow permissions) are
# not managed in Terraform. The GET /actions/permissions endpoint requires
# Administration scope, which the auto GITHUB_TOKEN used by the read-only plan
# and drift jobs does not have (403). These settings are left UI-managed,
# alongside default_workflow_permissions and can_approve_pull_request_reviews
# which the provider does not yet expose. Revisit when the project switches
# the plan job to an App-scoped token.

# Labels in use across issues/PRs. Declaring them keeps colour and description
# stable and prevents accidental removal.
resource "github_issue_label" "this" {
  for_each = {
    bug                    = { color = "d73a4a", description = "Something isn't working" }
    documentation          = { color = "0075ca", description = "Improvements or additions to documentation" }
    duplicate              = { color = "cfd3d7", description = "This issue or pull request already exists" }
    enhancement            = { color = "a2eeef", description = "New feature or request" }
    "good first issue"     = { color = "7057ff", description = "Good for newcomers" }
    "help wanted"          = { color = "008672", description = "Extra attention is needed" }
    invalid                = { color = "e4e669", description = "This doesn't seem right" }
    question               = { color = "d876e3", description = "Further information is requested" }
    wontfix                = { color = "ffffff", description = "This will not be worked on" }
    nightly                = { color = "d93f0b", description = "Nightly test failures" }
    "autorelease: pending" = { color = "ededed", description = "" }
    "autorelease: tagged"  = { color = "ededed", description = "" }
    dependencies           = { color = "0366d6", description = "Pull requests that update a dependency file" }
    "python:uv"            = { color = "2b67c6", description = "Pull requests that update python:uv code" }
    "user story"           = { color = "0e8a16", description = "User story for the Scrum board" }
    javascript             = { color = "168700", description = "Pull requests that update javascript code" }
  }
  repository  = github_repository.this.name
  name        = each.key
  color       = each.value.color
  description = each.value.description
}

# terraform-apply Environment: gates every `terraform apply` run behind a
# maintainer approval click and restricts applies to the main branch. This is
# the human-in-the-loop control ADR-0009 requires.
resource "github_repository_environment" "terraform_apply" {
  repository  = github_repository.this.name
  environment = "terraform-apply"
  # 60s cooling-off after approval before the apply step may start.
  wait_timer = 60
  reviewers {
    users = [data.github_user.maintainer.id]
  }
  deployment_branch_policy {
    custom_branch_policies = true
    protected_branches     = false
  }
}

resource "github_repository_environment_deployment_policy" "main_only" {
  repository     = github_repository.this.name
  environment    = github_repository_environment.terraform_apply.environment
  branch_pattern = "main"
}

# ponytail: the existing environments (codecov, github-pages, pypi,
# release-please) are owned by the workflows that created them and are left
# unmanaged here to avoid drift on the first plan. Import them into Terraform
# only when a maintainer wants to version them too.
