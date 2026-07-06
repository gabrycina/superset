# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Governance smoke tests for the experimental SAML SSO demo provider.

These tests pin the *current* behaviour of ``register_sso_provider`` so that the
demo stub cannot silently change shape. They intentionally do NOT assert any
security guarantees (signature validation, metadata_url validation, SSRF
protection); those are unmet and tracked in docs/governance/pr-9/. See that
directory for the tests a real implementation must add before wiring this into
authentication.
"""

from types import SimpleNamespace

from superset.security.demo_sso_provider import register_sso_provider


def _fake_app() -> SimpleNamespace:
    return SimpleNamespace(config={})


def test_register_sso_provider_appends_metadata_url() -> None:
    app = _fake_app()
    url = "https://idp.example.com/saml/metadata"

    result = register_sso_provider(app, url)

    assert app.config["SSO_PROVIDERS"] == [url]
    assert result == {"provider": "saml", "metadata_url": url}


def test_register_sso_provider_preserves_existing_providers() -> None:
    existing = "https://idp1.example.com/metadata"
    app = SimpleNamespace(config={"SSO_PROVIDERS": [existing]})
    new_url = "https://idp2.example.com/metadata"

    register_sso_provider(app, new_url)

    assert app.config["SSO_PROVIDERS"] == [existing, new_url]
