# VoiceForge AI Studio - Security Architecture

- **Auth**: JWT (Stateless) + Refresh Tokens (Stateful/DB for revocation).
- **OAuth**: Google Login integration.
- **RBAC**: Middleware to check roles (Admin, Artist, Manager, Producer).
- **API Security**: Rate limiting per user/IP.
- **File Security**: UUIDs for filenames (no user-provided names), scanned for malware.
