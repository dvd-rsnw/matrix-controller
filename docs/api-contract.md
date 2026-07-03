# Train API Contract

The board polls a single endpoint (`TRAIN_API_URL`) and renders the first
two arrivals. Any backend that serves this shape works — the author's
implementation happens to proxy MTA GTFS-realtime data, but the board
doesn't care.

## Request

`GET <TRAIN_API_URL>` — no auth, no parameters. Polled every
`POLLING_INTERVAL` seconds (default 15).

## Response

`200 OK` with a JSON array, soonest arrival first:

```json
[
  { "line": "F", "status": "5 mins", "express": false },
  { "line": "G", "status": "12 mins", "express": false }
]
```

| Field | Type | Notes |
|---|---|---|
| `line` | string | `"F"` or `"G"` get colored bullets and line names; anything else renders as plain text |
| `status` | string | `"N mins"` renders right-aligned with a fixed suffix; `"Now"` or any short string (≤7 chars) renders as-is |
| `express` | boolean | optional, default `false`; express F trains get the MTA diamond |

Extra fields are ignored. Extra array entries beyond the first two are
ignored. On non-200 responses, malformed payloads, or timeouts (5 s) the
board shows "No train data" and keeps polling.
