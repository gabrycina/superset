# Rollback Plan — PR #9: Experimental SAML SSO login provider

## What this change introduces
- One new file: `superset/security/demo_sso_provider.py` (function
  `register_sso_provider`).
- No database migrations, no schema changes, no dependency changes, no config
  defaults changed. The function is **not imported or called** anywhere in the
  tree.

Because the code is not wired into any import path or auth flow, reverting it is
low-risk and requires no data or migration cleanup. The steps below are ordered
from fastest/safest to most complete.

## Pre-rollback checks
```bash
# Confirm nothing else started importing the module before you revert.
git grep -n "demo_sso_provider\|register_sso_provider" -- 'superset/**' 'tests/**'
# Confirm no runtime config was set that references it.
grep -R "SSO_PROVIDERS" superset/config.py docker/ helm/ 2>/dev/null
```
If either returns matches that were added after this PR, revert those callers
first (or the app will fail to import after the file is removed).

## Option A — Revert the merge commit (preferred, git-native)
```bash
git checkout master && git pull --ff-only
# If PR #9 was merged as a merge commit:
git revert -m 1 <merge_commit_sha>
# If it was squash-merged (single commit):
git revert <squash_commit_sha>
git push origin master
```
Then redeploy master through the normal pipeline.

## Option B — Revert the PR from the GitHub UI
Open PR #9 → "Revert" → merge the generated revert PR. Equivalent to Option A.

## Option C — Manual removal (if revert conflicts)
```bash
git checkout -b revert/pr-9 master
git rm superset/security/demo_sso_provider.py
git rm -r docs/governance/pr-9   # optional: drop governance docs too
git commit -m "revert(security): remove experimental SAML SSO demo provider (PR #9)"
git push origin revert/pr-9
# open + merge PR
```

## Deploy / runtime rollback
- **Container/k8s:** roll back to the previously deployed image tag /
  `helm rollback superset <previous_revision>`. No migration downgrade needed.
- **No `superset db downgrade` required** — this PR adds no Alembic migration.
- If any operator had set `SSO_PROVIDERS` in `superset_config.py`, remove that
  entry as part of the deploy; it is inert without the function but should not be
  left dangling.

## Post-rollback verification
```bash
# Module is gone / not importable:
python -c "import importlib, sys; \
  print('present' if importlib.util.find_spec('superset.security.demo_sso_provider') else 'removed')"
# App boots and health check passes:
curl -f http://localhost:8088/health
# No lingering references:
git grep -n "register_sso_provider" || echo "clean"
```

## Blast radius / rollback risk
- **Risk: minimal.** Dead code with no callers, no data, no migrations. Reverting
  cannot corrupt state or lock out existing (non-SSO) logins.
- **Only real risk** is if downstream commits started importing the module —
  covered by the pre-rollback grep above.
