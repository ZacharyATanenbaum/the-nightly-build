# Editorial review: feature/passkeys-recovery-gap (editor/01)

## Correct

The thesis is that a passkey's domain-bound signature governs sign-in, while credential-provider recovery and website-account recovery apply different tests after a loss. W3C supports the domain boundary. NIST names recovery as a separate ceremony and identifies sync-service recovery as a threat. Apple's keychain document supports the provider-side example. Google, Microsoft and FIDO support the website-side alternatives. The federal AAL2 paragraph explicitly limits NIST's mandatory rule to its own context. Every printed source address resolves; none is a search or fetch proxy.

## Reads well

The draft defines a relying-party identifier where it first matters and follows the two recovery routes in order. I removed a generic closing claim about having a “security story” and replaced it with a conditional email-recovery example that makes the consequence testable. The voice remains a restrained account of implementation choices. The headline says recovery *can* bypass a passkey, and the article identifies the condition under which it can.

## The experience

The rendered preview has a clear headline, readable dek and visible citations. The comparison table separates the credential provider from the website more quickly than another paragraph would. The piece gives the reader a two-question test for recovery policies that no single cited document states in that form.

## Edits

- Replaced the final generic paragraph with a conditional account-recovery sequence grounded in the Google, FIDO and NIST sources.
- Restamped the word count and reading time after the edit.

## Decision

approve: the article's conditional conclusion follows the six opened sources, and the final local proof has no blocks or warnings.
