# SafeTask AI - Live Continuity State

The Live Continuity Rail protects active live camera obligations while the agent performs review work.

## Protected Live Shot Object

| Field | Type | Description |
|---|---|---|
| `camera_id` | String | Live camera identifier, such as `Camera 42`. |
| `location` | String | Zone or operational area covered by the camera. |
| `status` | String | Current live protection status, such as `LIVE | PROTECTED`. |
| `protected_since` | String | Time the user marked the live shot as protected. |
| `last_interaction` | String | Last time the user focused or updated the protected shot. |

## Behavior Rules

- Review clips open as PiP by default.
- Review clips do not silently replace protected live shots.
- Replacing a protected live shot requires explicit confirmation.
- A protected live shot can be restored to focus with one user action.
- If protected live shots and review clips are active at the same time, SafeTask shows a non-punitive coverage reminder.

## Coverage Reminder

The coverage reminder is a workload cue, not a discipline flag. It should help an agent or supervisor notice when review work and protected live coverage are happening at the same time. The message should recommend preserving PiP review or requesting coverage support if live activity increases.
