# Security and privacy

## Source publication boundary

The repository contains synthetic project metadata only. Runtime events are ignored. It does not bundle credentials, model prompts/responses, user accounts, private project memory, transcripts, or operational logs.

## Local runtime boundary

- The server binds to `127.0.0.1` by default.
- Observer routes are read-only.
- No model provider or shell executor is included.
- Patch application records a workflow state transition; it does not edit files.
- Identifiers and event types are allowlisted.

This design is not production hardened. A hosted multi-user version would require authentication, authorization, transport security, rate limiting, durable concurrency controls, audit-retention policy, and deployment-specific threat modeling.
