# Event model

Each JSON event has a unique identifier, project identifier, supported event type, payload object, UTC timestamp, and contiguous positive logical clock. The store rejects unsupported event types, unsafe identifiers, duplicate identifiers, and broken clock sequences.

The synthetic golden path is:

1. `project_created`
2. `goal_created`
3. `iteration_started`
4. `agent_response_received`
5. `approval_requested`
6. `approval_granted`
7. `patch_previewed`
8. `patch_applied`
9. `verification_passed`
10. `iteration_completed`

Replay folds this sequence into a deterministic projection. The projection hash covers the canonical state, not timestamps or event identifiers.

