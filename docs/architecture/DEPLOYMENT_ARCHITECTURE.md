# VoiceForge AI Studio - Deployment Architecture

- **Environments**: Dev (Docker Compose), Staging, Prod.
- **Scaling**: 
  - Backend: Stateless HTTP service.
  - Worker: Horizontal auto-scaling based on Redis queue depth (K8s HPA or similar).
- **Secrets**: Managed via environment variables, injected at runtime.
