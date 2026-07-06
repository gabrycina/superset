# Test Coverage — PR #9: Experimental SAML SSO login provider

## State of tests in the PR as submitted
**The PR shipped no tests.** The only file was
`superset/security/demo_sso_provider.py`; nothing under `tests/` was added or
changed. For a change classified critical (touches authentication), zero test
coverage is inadequate.

## What this governance pass added
A minimal characterization/smoke test that pins the stub's current behaviour so
it cannot silently drift:

- `tests/unit_tests/security/demo_sso_provider_test.py`
  - `test_register_sso_provider_appends_metadata_url` — asserts the URL is
    appended to `app.config["SSO_PROVIDERS"]` and the returned dict shape.
  - `test_register_sso_provider_preserves_existing_providers` — asserts existing
    providers are preserved (append, not overwrite).

Run:
```bash
pytest tests/unit_tests/security/demo_sso_provider_test.py
```
These are behavioural pins only. They **do not** assert any security property,
because the stub implements none.

## Tests that MUST be added before this is wired into authentication
These are gating requirements (see `security_checklist.md` / `threat_model.md`),
not covered by the current stub:

1. **`metadata_url` validation**
   - rejects non-`https` schemes;
   - rejects loopback / link-local / cloud-metadata (169.254.169.254) / private
     hosts (SSRF guard) — negative tests per host class.
2. **SAML assertion validation** (once parsing exists)
   - accepts an assertion correctly signed by the metadata cert;
   - rejects unsigned / wrong-key / tampered assertions;
   - rejects wrong `Audience`/`Destination`;
   - rejects expired / not-yet-valid / replayed assertions (`NotBefore`,
     `NotOnOrAfter`, `InResponseTo`).
3. **XML hardening** — XXE / DTD / entity-expansion payloads are rejected.
4. **Role mapping** — IdP attributes map only to allow-listed roles; no implicit
   Admin; unknown attributes → least privilege.
5. **Audit logging** — provider registration and auth decisions emit audit
   records with the expected fields (and never log raw assertions/keys).
6. **Session** — session id is regenerated on SSO login (fixation).
7. **Authorization of the registration entry point** — only an operator/Admin
   principal can register a provider (integration test against the eventual
   caller), mapped to the `SECURITY.md` matrix row.

Prefer unit tests, then integration tests (per repo testing guidance); add
Playwright E2E only for the end-to-end login flow once implemented.

## Verdict
Coverage is **inadequate for merge into an enabled state.** The added smoke test
makes the stub's behaviour explicit, but the security-critical tests above are
required before `register_sso_provider` is invoked from authentication.
