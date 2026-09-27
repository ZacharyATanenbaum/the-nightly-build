# Evidence: feature/passkeys-recovery-gap

The opened records support a narrow conclusion: WebAuthn prevents a credential from authenticating to an unrelated domain, while recovery is a separate decision made by both the passkey provider and the website. They do not measure how often recovery is attacked or show that every fallback is weak.

## Sources

URL: https://www.w3.org/TR/webauthn-3/
Kind: primary; W3C defines the WebAuthn protocol.
Establishes: A public-key credential can authenticate only for its registered RP ID; the website must validate the origin of an assertion.
Paraphrase: The RP ID identifies the website scope. Registration stores a public key that verifies later assertions signed with the private key.
Locators: terminology, “Relying Party Identifier” and “Public Key Credential”; §13.4.9, validating the origin of a credential.

URL: https://pages.nist.gov/800-63-4/sp800-63b.html
Kind: primary; NIST authors the federal authentication guidance.
Establishes: Recovery is distinct from sign-in. At AAL2, the standard gives combinations of recovery codes or reproofing, and requires recovery notifications. The syncable-authenticator section identifies cloud recovery as a potential weakness.
Paraphrase: NIST calls for a separate recovery ceremony when a subscriber loses authenticators; account recovery can bind a new authenticator. Its syncable-authenticator threat table calls out unauthorized access to the sync fabric and its recovery process.
Locators: §4.2 Account Recovery, especially “Recovery at AAL2”; Appendix B, Table 5 and “Example.” Federal requirements are not universal consumer-site rules.

URL: https://fidoalliance.org/wp-content/uploads/2024/05/Synced-Passkey-Deployment_-Emerging-Practices-for-Consumer-Use-Cases_2024-May-31.pdf
Kind: primary; FIDO Alliance authors consumer deployment guidance for relying parties.
Establishes: A website may offer other passkeys, password plus SMS OTP, or an email magic link when a passkey cannot be used. Stronger identity proofing can be needed for sites that require passkeys. FIDO warns that recovery can become a point of compromise.
Paraphrase: The paper separates the website's record from the provider's stored private key; deletion at one does not automatically delete the other.
Locators: §5.4 and §5.5, PDF pages 18–19 in the viewer.

URL: https://developers.google.com/identity/passkeys/ux/user-journeys
Kind: primary; Google's design guidance to services adopting passkeys.
Establishes: Google advises setting up an account recovery method at registration. Email, phone or federated login are examples, and people can hold multiple passkeys.
Paraphrase: A fallback lets users regain access if all their passkeys are unavailable, but the website chooses that fallback.
Locators: “Creating new accounts with passkeys,” “Managing passkeys,” and “Have an email or phone fallback.”

URL: https://learn.microsoft.com/en-us/aspnet/core/security/authentication/passkeys/?view=aspnetcore-10.0
Kind: primary; Microsoft's documentation describes the ASP.NET Core Identity implementation.
Establishes: The built-in template requires a backup method; for passkey-only apps Microsoft suggests recovery codes, email recovery, multiple passkeys and a backup-state check. These are recommendations for this implementation, not a guarantee across all sites.
Paraphrase: Registration places a public key on the server; authentication asks the private key to sign a fresh challenge.
Locators: “Attestation,” “Assertion,” and “Account recovery.”

URL: https://support.apple.com/en-ca/guide/security/sec1c89c6f3b/web
Kind: primary; Apple's platform security documentation describes iCloud Keychain.
Establishes: Apple says iCloud Keychain syncs passkeys between devices with end-to-end encryption and has a recovery service for lost-device cases.
Paraphrase: Provider-side recovery is separate from the website's own recovery flow. Encryption of synced items does not itself answer who may re-enroll at a website.
Locators: “iCloud Keychain security overview,” opening two paragraphs.

## Contradictions

Google and Microsoft list email recovery as a practical way to avoid lockout. NIST's federal AAL2 recovery requirements demand two distinct recovery methods, one method plus a bound authenticator, or renewed identity proofing. The difference is the assurance level and intended deployment, not a factual disagreement. Apple describes encrypted sync and recovery as protection; NIST still treats unauthorized sync-fabric recovery as a threat to evaluate. Both can be true.

## Numbers

No prevalence or attack-rate figure is supported. Avoid percentages and broad frequency claims. NIST's “two” recovery codes at AAL2 is a normative option for that level, not an observed usage number.

## Limits

- The records do not establish that a particular website's recovery flow can be bypassed.
- The records do not compare real-world compromise rates of passwords, synced passkeys and device-bound keys.
- A consumer website need not implement NIST federal AAL2 recovery rules.

## Source assets

None found that would explain the two authorities better than a short comparison table built from the cited text.

## Discarded

https://www.troyhunt.com/passkeys-for-normal-people/: a useful first-person implementation account and writing exemplar, but not the primary owner of protocol or platform claims.
