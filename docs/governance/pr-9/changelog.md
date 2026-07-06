# Changelog — PR #9: Experimental SAML SSO login provider

## Added
- **Experimental (demo) SAML SSO provider seam.** New helper
  `register_sso_provider(app, metadata_url)` in
  `superset/security/demo_sso_provider.py` records a SAML provider's metadata URL
  under `app.config["SSO_PROVIDERS"]`. This is an early, experimental stub and is
  **not enabled by default** and **not wired into authentication**.

## User-facing impact
- **None by default.** No existing login flow (DB, OAuth, LDAP, REMOTE_USER)
  changes. The new function is not invoked anywhere; deploying this PR does not
  alter runtime behavior.

## Notes / caveats
- ⚠️ **Do not use in production.** The current implementation performs no SAML
  assertion validation, no `metadata_url` validation/SSRF protection, no audit
  logging, and no role mapping. See `docs/governance/pr-9/threat_model.md` and
  `security_checklist.md`.
- No database migration, dependency, or configuration default is introduced by
  this change.

## Conventional-commit suggestion for the PR title
`feat(security): add experimental SAML SSO provider seam (demo, disabled)`
