#!/usr/bin/env bash
# Applies repository settings, security features and rulesets via the GitHub API.
# Idempotent: safe to re-run. Requires an authenticated `gh` with admin rights on the repo.
#
#   scripts/setup-github.sh            # current repo
#   REPO=owner/name scripts/setup-github.sh
set -euo pipefail

REPO="${REPO:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
GITHUB_ACTIONS_APP_ID=15368   # status checks must come from GitHub Actions
ADMIN_ROLE_ID=5               # built-in "admin" repository role

echo "==> Configuring $REPO"

echo "--> Merge settings and features"
gh api -X PATCH "repos/$REPO" --silent --input - <<'JSON'
{
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "squash_merge_commit_title": "PR_TITLE",
  "squash_merge_commit_message": "PR_BODY",
  "delete_branch_on_merge": true,
  "allow_auto_merge": true,
  "allow_update_branch": true,
  "has_wiki": false,
  "has_projects": false,
  "security_and_analysis": {
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" }
  }
}
JSON

echo "--> Actions: read-only default token, allow release-please to open PRs"
gh api -X PUT "repos/$REPO/actions/permissions/workflow" --silent --input - <<'JSON'
{ "default_workflow_permissions": "read", "can_approve_pull_request_reviews": true }
JSON

echo "--> Dependabot alerts + security updates, private vulnerability reporting"
gh api -X PUT "repos/$REPO/vulnerability-alerts" --silent
gh api -X PUT "repos/$REPO/automated-security-fixes" --silent
gh api -X PUT "repos/$REPO/private-vulnerability-reporting" --silent

# Create or update a ruleset by name.
upsert_ruleset() {
  local name="$1" body="$2" id
  id="$(gh api "repos/$REPO/rulesets" --jq ".[] | select(.name == \"$name\") | .id")"
  if [[ -n "$id" ]]; then
    echo "--> Updating ruleset '$name' ($id)"
    gh api -X PUT "repos/$REPO/rulesets/$id" --silent --input - <<<"$body"
  else
    echo "--> Creating ruleset '$name'"
    gh api -X POST "repos/$REPO/rulesets" --silent --input - <<<"$body"
  fi
}

upsert_ruleset "main" "$(cat <<JSON
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [
    { "actor_id": $ADMIN_ROLE_ID, "actor_type": "RepositoryRole", "bypass_mode": "pull_request" }
  ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "ci-ok", "integration_id": $GITHUB_ACTIONS_APP_ID },
          { "context": "pr-title", "integration_id": $GITHUB_ACTIONS_APP_ID }
        ]
      }
    }
  ]
}
JSON
)"

upsert_ruleset "release-tags" "$(cat <<'JSON'
{
  "name": "release-tags",
  "target": "tag",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/tags/v*"], "exclude": [] } },
  "bypass_actors": [],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "update" }
  ]
}
JSON
)"

echo "==> Done"
