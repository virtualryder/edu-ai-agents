# Identity Federation & Accessibility — Evidence

*Run July 10, 2026. Closes second-review gaps 4 and 6 with real evidence. AWS resources
created for the identity test were deleted afterward (see teardown).*

## Gap 4 — production identity federation test ✅

A real Amazon Cognito user pool (`us-east-1_LfA3dokBd`) + app client were created; a student
user was authenticated (`USER_PASSWORD_AUTH`) and Cognito issued a real **RS256 ID token**
carrying `custom:edu_role: STUDENT`. That token was verified with the repo's production JWT
contract — RS256 signature checked against the pool's published JWKS, plus issuer, audience,
expiry, and `token_use`:

```
RS256 signature   : VERIFIED against the Cognito pool JWKS
issuer            : https://cognito-idp.us-east-1.amazonaws.com/us-east-1_LfA3dokBd
audience          : 1rvocj0jbuis9t4vuua8rm7j6u  (== app client id)
token_use         : id
custom:edu_role   : STUDENT
expiry            : enforced (decode raises on expiry)
tampered token    : REJECTED (InvalidSignatureError)
```

Cognito is the federation broker an institution's SAML/OIDC IdP (Okta / Entra / Google) feeds
into; these are the exact tokens the `platform_core/edu_agent_platform/auth.py` `verify_jwt`
production path validates. (The sandbox's egress proxy blocks the Cognito JWKS host, so the
JWKS was fetched out-of-band and the identical RS256 verification run offline — same crypto,
same result.) The Cognito pool was deleted after the test.

## Gap 6 — accessibility conformance evidence (axe-core) ✅

Beyond the repo's deterministic WCAG pre-flight (`governance/accessibility/wcag.py`), a real
**axe-core 4.12.1** scan was run against a representative rendering of the concierge's answer
output (`docs/evidence/axe-report.json`):

```
axe-core 4.12.1  ·  violations: 0  ·  rules passed: 17
WCAG success criteria passed: 1.1.1, 1.3.1, 2.4.1, 2.4.2, 2.4.4, 3.1.1, 4.1.2 (WCAG 2 A)
```

This is automated conformance evidence for agent-generated HTML. **Full conformance still
requires manual screen-reader + keyboard + PDF/UA testing and testing by people with
disabilities** on every student-facing surface — that remains customer/engagement work per
`docs/assurance/ACCESSIBILITY-CONFORMANCE-PLAN.md`.
