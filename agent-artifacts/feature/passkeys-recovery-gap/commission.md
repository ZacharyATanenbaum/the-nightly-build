# Commission: feature/passkeys-recovery-gap

The owner asked for the paper's first published article and supplied no subject. The Feature series permits a durable technology question. This piece asks what security a passkey actually provides when its owner loses access and needs to recover either the passkey store or the website account.

Establish the WebAuthn boundary at ordinary sign-in, then trace two separate recovery paths: the credential manager that syncs a passkey and the website that accepts it. Explain how a website's fallback can admit a claimant without the passkey, and how strong recovery rules can preserve the gain. Distinguish a compromised provider from a lost device. Do not claim that every email fallback is exploitable or that every service uses one. Do not claim a measured attack rate; the opened sources do not provide one.

The contribution is a side-by-side account of the two recovery authorities that the standards and implementation guides discuss separately. Use the article template. The slug is `passkeys-recovery-gap`. The archive is empty, so there is no prior coverage or recurring structure to avoid. The latest opened sources are W3C WebAuthn Level 3, NIST SP 800-63B-4, FIDO's consumer deployment paper, and implementation guidance from Google, Microsoft and Apple.

The article should be a reported explanatory feature for a technically literate general reader. The closing judgment must follow from the two recovery paths. Keep the federal scope of NIST's mandatory language explicit.
