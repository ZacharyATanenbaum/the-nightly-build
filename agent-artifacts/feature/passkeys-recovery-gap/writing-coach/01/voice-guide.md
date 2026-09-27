# Voice guide: feature/passkeys-recovery-gap

## How this piece should sound

Use Schneier's habit of naming the actor and the mechanism before judging a security design. Let a concrete account-loss scenario expose what the cryptographic sign-in ceremony does and where it ends. Troy Hunt's useful move is to inspect the actual path a person can take through a service; keep that scrutiny, without borrowing his conversational exclamations. Julia Evans makes an abstract browser rule visible by walking through a specific request. Use that clarity for the difference between a website account and a synced credential store, in the paper's more restrained register.

## Bruce Schneier, "Customers, Passwords, and Web Sites"

Source: https://www.schneier.com/essays/archives/2004/07/customers_passwords.html

> "Criminals follow money."

Checked: source page, retrieved 2026-09-27, opening paragraph. The sentence identifies an actor and motive without staging a grand claim. It starts from a testable account of incentives.

> "This is why criminals have turned to stealing passwords."

Checked: source page, retrieved 2026-09-27, paragraph after the discussion of online guessing. The conclusion comes after the mechanism. Schneier trusts the reader to connect the steps.

## Troy Hunt, "Passkeys for Normal People"

Source: https://www.troyhunt.com/passkeys-for-normal-people/

> "This is up to the service implementing them"

Checked: source page, retrieved 2026-09-27, paragraph after the WhatsApp setup. Hunt points at an implementation decision rather than treating the standard as a complete product. That distinction matters here.

> "However, there's a problem: I still have a password on the account"

Checked: source page, retrieved 2026-09-27, LinkedIn login section. The first-person observation is narrow enough to test. The article should report equivalent decisions through documents, without adopting Hunt's first-person voice.

## Julia Evans, "Using the Strict-Transport-Security header"

Source: https://jvns.ca/blog/2017/04/30/using-strict-transport-security/

> "But a lot of sites do have private content, and should always use encryption!"

Checked: source page, retrieved 2026-09-27, HTTPS section. Evans moves from her own site to the case where the rule matters. Use the movement from a concrete case to its boundary, with quieter punctuation.

> "I don’t want ads injected into my site!"

Checked: source page, retrieved 2026-09-27, why she enabled HSTS. The sentence ties a security control to a specific unwanted outcome. Keep that specificity when explaining recovery controls.
