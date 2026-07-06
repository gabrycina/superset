# Migration & Deploy Plan — PR #9: Experimental SAML SSO login provider

## Summary
This PR adds `superset/security/demo_sso_provider.py` only. There is **no Alembic
database migration**, **no schema change**, and **no dependency change**. There is
therefore no data backfill and no DB downgrade to plan. The "migration" here is
purely a code deploy of an inert function plus (future) configuration.

## Ordered deploy steps
1. **Merge & build** the image containing the new module (after governance
   sign-off — see threat model / security checklist).
2. **Deploy** through the normal pipeline (rolling deploy / `helm upgrade`). No
   pre- or post-deploy migration job is needed:
   ```bash
   # NOT required for this PR — no migration present:
   # superset db upgrade
   ```
3. **Verify boot & health** on each replica:
   ```bash
   curl -f http://<host>:8088/health
   ```
4. **No config change ships by default.** `register_sso_provider` is not called
   anywhere, so behavior is unchanged after deploy. Enabling SSO is a *separate,
   later* operator action once the real implementation exists.

## Enabling the provider (future, gated)
When the full implementation lands, enabling is an operator step, ideally behind
a feature flag and applied after the code deploy:
```python
# superset_config.py (illustrative — do NOT enable with the current stub)
from superset.security.demo_sso_provider import register_sso_provider
register_sso_provider(app, "https://idp.example.com/saml/metadata")
```
Roll this out to a canary/staging tenant first, validate a full SSO login, then
promote.

## Forward / backward compatibility
- **Backward compatible:** existing `AUTH_DB`/OAuth/LDAP logins are untouched; no
  stored data or session format changes. Older nodes in a mixed-version cluster
  are unaffected because the function is never invoked.
- **Forward compatible:** `app.config.setdefault("SSO_PROVIDERS", [])` is additive
  and tolerant of the key being absent; it will not clobber an existing value.
- **Note for the real implementation:** the current `SSO_PROVIDERS = list[str]`
  shape may need to become a list of structured provider configs. Treat the shape
  as unstable; version or namespace it before external reliance to avoid a
  breaking config migration later. Record any breaking change in `UPDATING.md`.

## Rollback
See `rollback_plan.md`. Because there is no migration, rollback is a code
revert + redeploy (or `helm rollback`) with no `db downgrade`.

## Deploy risk
Minimal — inert code, no migration, no dependency, no default behavior change.
