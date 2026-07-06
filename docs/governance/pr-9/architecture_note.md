# ADR — PR #9: Experimental SAML SSO login provider

- **Status:** Proposed (experimental / demo stub)
- **PR:** #9 — Add experimental SAML SSO login provider
- **Change:** new module `superset/security/demo_sso_provider.py`

## Context
Superset authenticates via Flask-AppBuilder (FAB), which already supports
`AUTH_OAUTH`, `AUTH_LDAP`, `AUTH_REMOTE_USER`, and `AUTH_DB`. Operators have asked
for SAML 2.0 SSO so Superset can join enterprise IdPs (Okta, Azure AD, ADFS).
This PR is a first, deliberately minimal step: a `register_sso_provider(app,
metadata_url)` function that records a SAML provider's metadata URL on
`app.config["SSO_PROVIDERS"]`. It is a stub — no metadata fetch, no assertion
validation, not yet wired into FAB's `SecurityManager`.

## Decision
Land a thin registration seam now (`register_sso_provider`) that captures the
*intent* and the config shape (`SSO_PROVIDERS`), gated behind change-governance
review, before building the full SAML flow. The function currently:
- appends `metadata_url` to `app.config.setdefault("SSO_PROVIDERS", [])`;
- returns `{"provider": "saml", "metadata_url": metadata_url}`.

This ADR records that the seam is intentionally inert and enumerates what a real
implementation must add before it can be enabled.

## Alternatives considered
1. **Use an existing SAML library end-to-end now**
   (`python3-saml` / `flask-appbuilder` OAuth-style provider). Rejected for this
   PR: larger dependency + security surface (see threat model); wanted the
   governance seam first. This is the expected follow-up.
2. **Rely on FAB `AUTH_REMOTE_USER` + an external SAML proxy** (e.g. mod_auth_mellon,
   oauth2-proxy). Viable operationally and keeps SAML parsing out of Superset,
   but pushes role mapping outside the app and doesn't give a native config.
   Kept as a documented deployment alternative, not chosen for the native path.
3. **Do nothing / OAuth-only.** Rejected: does not meet the SAML requirement.
4. **Custom `SecurityManager` subclass per deployment.** Rejected as the primary
   path: duplicative and error-prone across operators; a first-class provider is
   preferable.

## Consequences
### Positive
- Establishes the config contract (`SSO_PROVIDERS`) and a single registration
  entry point to build on.
- Small, reviewable diff; no migrations or dependencies added.

### Negative / risks
- The seam looks usable but enforces nothing (no signature/audience/time checks,
  no SSRF guard on `metadata_url`, no audit log, no role mapping). See
  `threat_model.md` and `security_checklist.md`. There is a real risk of it being
  wired in prematurely.
- `SSO_PROVIDERS` as an unbounded list on `app.config` is a placeholder shape,
  not a final design (no dedup, no per-provider settings, no enable flag).

### Follow-up work required before non-demo use
- Integrate with FAB `SecurityManager`; add SAML assertion validation via a
  vetted library.
- Validate/allow-list `metadata_url` (https-only, SSRF protection) before fetch.
- Explicit IdP-attribute → role mapping; audit logging; feature flag default-off.
- Docstrings/types per repo standards; unit + integration tests.

## References
- `superset/security/demo_sso_provider.py`
- `docs/governance/pr-9/threat_model.md`, `security_checklist.md`,
  `migration_plan.md`, `rollback_plan.md`, `tests.md`
- `SECURITY.md` (trust boundaries, role/capability matrix)
