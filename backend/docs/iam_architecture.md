# Identity and Access Management (IAM)

This document outlines the architecture for the VoiceForge IAM module.

## Core Capabilities
- **Authentication**: Email/Password, JWT (Access & Refresh tokens).
- **Session Management**: Secure rotating refresh tokens.
- **RBAC**: Role-based access control with permissions mapping.
- **Security**: Argon2id/bcrypt password hashing, account lockout protection.
- **Organizations**: Multi-tenant workspace architecture.
- **Auditing**: Comprehensive security event logging.
- **Rate Limiting**: Endpoint protection via Redis/SlowAPI constraints.

## Structural Flow
1. **User Registration**: Creates `User` (and implicitly a personal `Organization`).
2. **Login**: Validates credentials. Applies brute-force lockout if failed > 5 times.
3. **Token Issuance**: Returns short-lived `access_token` (JWT) and long-lived `refresh_token` (DB-backed).
4. **Token Rotation**: Swaps `refresh_token` for a new pair. Detects compromised token families and revokes all tokens for that user.
5. **Authorization**: API endpoints secured via `deps.require_permissions("project", "create")` ensuring the user holds a valid role inside the target `Organization`.

## Models
- `Organization` and `OrganizationMember`
- `RefreshToken`
- `RolePermission`
- Extends `User` with lockouts, verification, and active state tracking.
