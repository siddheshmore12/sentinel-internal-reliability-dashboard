# Sentinel Roadmap & Phasing

This document breaks down the project delivery into phases.

## Phase 1: Heart (Core State & Routing)
- Define Domain Entities (Service, HealthCheck, Incident)
- Build Pydantic validation boundaries
- Scaffold FastAPI endpoints with mock persistence

## Phase 2: Brain (Rules & Workers)
- Implement `asyncio` background worker
- Implement Strategy Pattern for extensibility (HTTP, TCP, Postgres checkers)
- Build Risk Assessment Logic for auto-triaging incidents
- Route real telemetry to PostgreSQL

## Phase 3: Skeleton (Frontend & Cache)
- Setup React SPA via Vite
- Wire Tanstack Query to REST endpoints
- Introduce Redis Caching layer to alleviate Dashboard load times
- Build components: Grid, Cards, ReCharts

## Phase 4: Senses (Observability & SRE)
- Expose `/metrics` proxy
- Provision Grafana Dashboards
- Automate MTTR measurement logs
- Containerize via Docker Compose

## Phase 5: Future Enhancements
- Introduce WebSockets for real-time pushing
- Add Slack Bot Integration for paging
- Build auth and SSO via OIDC
