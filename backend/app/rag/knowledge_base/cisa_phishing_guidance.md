# CISA Cybersecurity Guidance: Phishing Defense and Incident Response

## Overview of Phishing Tactics
Phishing is a form of social engineering where attackers deceive individuals into divulging sensitive information such as credentials, financial information, or personal identifiers. Common indicators include:
1. Urgent or threatening language demanding immediate account verification.
2. Typosquatted or visually deceptive domain names resembling familiar brands.
3. Unsolicited requests for password resets or multi-factor authentication codes.
4. Mismatched URLs where display text differs from the actual hyperlink destination.

## URL Structure Analysis
Attackers frequently exploit subtle lexical anomalies in URLs to evade detection:
- Using raw IP addresses instead of legitimate registered domain names.
- Creating excessive nested subdomains (e.g., `paypal.com.verification-update.net`) to disguise the genuine root domain.
- Applying URL encoding or percent-escaped characters to conceal executable or redirection parameters.
- Registering recently created top-level domains (TLDs) with low historical reputation.

## Remediation Steps if Credentials are Compromised
If a user submits credentials to a suspect phishing website:
1. **Immediate Password Reset**: Change the password on the genuine service immediately from a secure, trusted device.
2. **Revoke Active Sessions**: Log out of all active web and mobile sessions associated with the compromised account.
3. **Enable Phishing-Resistant MFA**: Upgrade to FIDO2 / WebAuthn hardware security keys or authenticator apps; avoid SMS-based OTPs where possible.
4. **Audit Account Activity**: Inspect recent transactions, login history, and email forwarding rules for unauthorized changes.
5. **Report the Threat**: Submit the malicious URL to the organization's security operations center (SOC) and public repositories such as CISA, Google Safe Browsing, and the Anti-Phishing Working Group (APWG).
