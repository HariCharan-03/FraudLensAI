# NIST Guidelines on Identity, Phishing Resistance, and Domain Validation

## NIST SP 800-63B Authentication and Authenticator Assurance
NIST provides definitive standards for counteracting modern social engineering and adversary-in-the-middle (AiTM) phishing proxies:
1. **Phishing-Resistant Authenticators (AAL3)**:
   - Cryptographically bound credentials (FIDO2 / WebAuthn, smart cards) that authenticate the origin domain directly during the cryptographic handshake.
   - Even if a user visits a deceptive phishing proxy, the browser sends the actual domain in the WebAuthn clientDataJSON, preventing credential replay against the authentic service.
2. **Adversary-in-the-Middle (AiTM) Reverse Proxies**:
   - Attackers deploy tools like Evilginx to intercept username, password, and session cookies simultaneously.
   - Traditional SMS or TOTP codes do not protect against AiTM proxies; only phishing-resistant MFA provides effective deterrence.

## Domain & Infrastructure Verification
NIST SP 800-177 recommends organizations enforce:
- Sender Policy Framework (SPF), DomainKeys Identified Mail (DKIM), and Domain-based Message Authentication, Reporting, and Conformance (DMARC) with `p=reject` policy.
- Continuous monitoring of Certificate Transparency (CT) logs to identify newly issued certificates for lookalike domains.
- Fast-flux and dynamic DNS detection to isolate rapidly shifting botnet IP addresses.
