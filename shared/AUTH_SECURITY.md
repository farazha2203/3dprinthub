# Authentication and Security
Google Login/reCAPTCHA may be used but must not be a single point of failure. If Google is blocked/unavailable, never bypass security; use an approved fallback such as SMS OTP or username/password with rate limiting, lockout/brute-force protection and secure recovery.

Document methods, fallback order, provider config, env-var names, session/token behavior, rate limits, audit logging, recovery and tests. Never commit secrets. Validate server-side. OTPs must expire and be single-use. Protect admin/privilege changes and test provider-outage behavior.
