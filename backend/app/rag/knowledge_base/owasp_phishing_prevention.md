# OWASP Phishing Defense and Web Application Guidance

## Technical Indicators of Malicious URLs
OWASP identifies several critical attack vectors involving URL abuse:
1. **Open Redirection**: Attackers append redirection parameters (e.g., `?redirect=http://evil.com`) to legitimate domains to bypass simple domain whitelists.
2. **IDN Homograph Attacks**: Utilizing lookalike internationalized characters (e.g., Cyrillic 'а' replacing Latin 'a') to spoof recognized corporate domains.
3. **Misleading Subdomains**: Placing brand names in subdomains while hosting malicious infrastructure on an unrelated apex domain.
4. **Credential Harvesting Forms**: Phishing landing pages designed to clone authentic authentication forms while submitting data to third-party endpoints.

## TLS/SSL Misconceptions
A common misconception is that the presence of an SSL/TLS certificate (HTTPS) guarantees a website is legitimate.
- Attackers easily obtain free, automated TLS certificates (e.g., through Let's Encrypt) for phishing domains.
- HTTPS guarantees transport layer encryption between the client and the server, but does NOT certify the malicious or benevolent intent of the server operator.
- Short certificate lifespans or mismatched Subject Alternative Names (SANs) are frequent signals of temporary throwaway infrastructure.

## Defensive Strategies
1. Content Security Policy (CSP) headers restricting form submissions (`form-action`).
2. Robust domain reputation monitoring and proactive detection of defensive registrations.
3. User awareness regarding address bar inspection and domain hierarchy verification.
