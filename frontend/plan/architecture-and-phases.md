# IBVAP Frontend Implementation Plan

## Overview
This document outlines the architecture, routing, component strategy, and phased implementation plan for the IBVAP (Intelligent Border Video Analytics Platform) Next.js 15 frontend. The frontend acts as a Command and Control (C2) hub, prioritizing situational awareness, real-time alerts, and hardware-agnostic configuration via virtual fences.

## Architecture & Integration Strategy
As defined in `server.md` and `docs/api-frontend-integration.md`:
1.  **Data Fetching (Reads):** Direct to Supabase PostgreSQL using `@supabase/ssr` (Next.js Server/Client components).
2.  **Real-time Updates:** Direct Supabase Realtime WebSocket subscriptions for `alerts` and `devices` tables.
3.  **Authentication:** Supabase Auth with session management via `proxy.ts`.
4.  **Control Plane (Writes/Config):** API calls to the FastAPI server (`backend/main.py`) for orchestrating changes that affect edge devices (e.g., updating virtual fences via SSE).
5.  **Media:** Direct Supabase Storage fetching via signed URLs for `evidence_path`.

---

## Route Structure

```
frontend/src/app/
├── (auth)/
│   └── login/                 # Supabase Auth Login Page
│
├── (dashboard)/               # Protected C2 Routes
│   ├── layout.tsx             # Tactical sidebar, global header, Real-time connection health
│   │
│   ├── page.tsx               # (/) LIVE COMMAND CENTER
│   │                          # Server: Fetch initial KPIs (Intrusions today, Active cameras).
│   │                          # Client: Realtime Alert Ticker, Map of online devices.
│   │
│   ├── alerts/                # (/alerts) INVESTIGATION & EVIDENCE
│   │   ├── page.tsx           # Server: Paginated/filtered query on `alerts` JOIN `detections`.
│   │   └── [id]/page.tsx      # Client: <EvidenceViewer /> (Storage Image + SVG BBox overlays).
│   │
│   ├── intelligence/          # (/intelligence) WATCHLISTS & PROFILING
│   │   ├── faces/page.tsx     # Server: Query `known_faces`. Client: Upload to FastAPI for embedding.
│   │   └── vehicles/page.tsx  # Server: Query `watchlist_plates`. Client: Direct Supabase INSERT.
│   │
│   ├── infrastructure/        # (/infrastructure) DEVICES & CAMERA CONFIG
│   │   ├── page.tsx           # Server: Grid of `devices` and `cameras`. Status indicators.
│   │   └── [id]/settings/     # Client: <VirtualFenceCanvas />. Draws ROIs. PUT to FastAPI.
│   │
│   └── analytics/             # (/analytics) REPORTING & TRENDS
│       └── page.tsx           # Server: Aggregation queries/RPCs. Client: Charts (Intrusions over time, heatmaps).
```

---

## Implementation Chunks

### Chunk 1: Foundations & Auth
**Goal:** Setup UI infrastructure, secure the app, and establish the tactical layout.
*   **Tasks:**
    *   Initialize `shadcn/ui` and configure a dark "tactical" Tailwind theme.
    *   Build the `(auth)/login` page wired to Supabase Auth.
    *   Implement the `(dashboard)/layout.tsx` (Sidebar navigation, header with user profile).
    *   Verify `proxy.ts` correctly protects the dashboard routes.

### Chunk 2: Infrastructure Management & Virtual Fences
**Goal:** Allow operators to see connected devices and configure the AI detection zones (the core of the problem statement).
*   **Tasks:**
    *   Build `/infrastructure/page.tsx` to list devices and their online status from the `devices` table.
    *   Build the device details page showing connected cameras.
    *   Implement the `<VirtualFenceCanvas />` component in `/infrastructure/[id]/settings`.
    *   Wire the canvas save button to `PUT /api/v1/control/devices/{id}/settings` on the FastAPI backend.

### Chunk 3: Live Command Center & Real-time Alerts
**Goal:** Deliver immediate situational awareness without manual video monitoring.
*   **Tasks:**
    *   Build the main `/` Dashboard page.
    *   Implement the `<RealtimeAlertFeed />` component using `@supabase/supabase-js` `on('postgres_changes')` to stream new alerts.
    *   Implement KPI cards (fetching aggregates from Supabase).
    *   (Optional but recommended) Implement a simple Map component displaying device coordinates.

### Chunk 4: Alert Investigation & Evidence Viewing
**Goal:** Allow deep dives into specific security incidents.
*   **Tasks:**
    *   Build `/alerts/page.tsx` with filtering (by device, date, threat level).
    *   Build `/alerts/[id]/page.tsx` to view a single alert.
    *   Implement the `<EvidenceViewer />` that fetches the image from Supabase Storage and draws bounding boxes based on the `detections` table data.

### Chunk 5: Intelligence & Analytics
**Goal:** Manage known threats and view long-term trends.
*   **Tasks:**
    *   Build `/intelligence/faces` and `/intelligence/vehicles` CRUD interfaces.
    *   Wire the face upload form to the FastAPI `POST /api/v1/faces/known` endpoint.
    *   Build `/analytics/page.tsx` using a charting library (e.g., Recharts) to visualize data (e.g., alerts by hour/day) fetched via Supabase RPCs or direct SQL aggregations.
