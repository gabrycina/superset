"""Experimental SSO login provider (demo).

Adds a SAML-based single sign-on provider to the security manager.
Touches authentication — requires full change-governance review.
"""


def register_sso_provider(app, metadata_url):
    # NOTE: demo stub for the governance workflow.
    app.config.setdefault("SSO_PROVIDERS", []).append(metadata_url)
    return {"provider": "saml", "metadata_url": metadata_url}
