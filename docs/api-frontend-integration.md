# Frontend API Integration & Supabase Usage

## Direct Supabase Usage vs. FastAPI Server

**Recommendation: Use direct Supabase for most frontend operations.**

According to the architecture defined in `server.md`, the frontend is built with **Next.js 15 (App Router)** and Supabase is heavily utilized for authentication, real-time updates, and data fetching. 

**When to use Supabase directly from the Frontend:**
1.  **Authentication:** Use Supabase Auth for operator login, logout, and session management.
2.  **Data Fetching (Queries):** Directly query PostgreSQL tables (e.g., `devices`, `alerts`, `face_results`) using the `supabase-js` or `@supabase/ssr` client. This leverages Row-Level Security (RLS) and is faster/simpler than proxying through FastAPI.
3.  **Real-time Subscriptions:** Use Supabase Realtime to listen for `INSERT` or `UPDATE` events on tables like `alerts` and `devices` to update the UI instantly.
4.  **Storage Retrieval:** Use Supabase Storage to get signed URLs for evidence images directly.

**When to use the FastAPI Server from the Frontend:**
The FastAPI server acts as the control plane for the edge devices and the ingestion engine. The frontend should call FastAPI **only** for operations that require side effects affecting the edge devices or complex backend orchestration:
1.  **Updating Device Settings:** When an operator saves new camera settings or zones, the frontend should `PUT` to the FastAPI server, which will save to the DB and push the config to the edge device via SSE.
2.  **Triggering AI/Heavy Compute:** If you need to manually trigger face matching or add a known face to the watchlist (which requires running the embedding model), this goes through FastAPI.

---

## Required Endpoints & Supabase Tables for Frontend

### 1. Devices & Cameras
**Direct Supabase Tables:**
*   `devices`: Fetch list, online status, last seen.
*   `cameras`: Fetch cameras linked to a device.
*   `device_settings`: Fetch current configuration for UI state.

**FastAPI Endpoints (Control Plane):**
*   `PUT /api/v1/devices/:id/settings`: Update runtime settings (zones, thresholds). FastAPI updates DB and triggers SSE to the edge.

### 2. Alerts & Evidence
**Direct Supabase Tables:**
*   `alerts`: Query with filters (device, time, feature). Subscribe for real-time inserts.
*   `detections`: Fetch bounding boxes for a specific alert.
*   `face_results` / `anpr_results`: Fetch AI metadata for alerts.

**Supabase Storage:**
*   Bucket `evidence`: Generate signed URLs for `alerts.evidence_path`.

### 3. AI & Watchlists
**Direct Supabase Tables:**
*   `known_faces`: Fetch watchlist.
*   `watchlist_plates`: Fetch flagged plates.
*   `face_results` / `anpr_results`: Review unmatched or flagged results.

**FastAPI Endpoints (Compute):**
*   `POST /api/v1/faces/known`: Upload a new reference photo. FastAPI runs the ArcFace model, extracts the embedding, and saves to `known_faces`.

### 4. Dashboard Analytics
**Direct Supabase Tables / RPC:**
*   You can create PostgreSQL functions (RPCs) to aggregate stats (e.g., alerts per hour) and call them directly via `supabase.rpc('get_dashboard_stats')`.

### 5. Authentication (Supabase Auth)
*   Login, Role management, Session handling all done directly via Supabase Auth client in Next.js.

---

## Summary of Frontend Flow

1.  **Auth:** Next.js uses `@supabase/ssr` to authenticate the user and get a session.
2.  **Load Dashboard:** Frontend queries the `devices` and `alerts` tables directly via Supabase client.
3.  **Real-time:** Frontend subscribes to the `alerts` table via Supabase Realtime to update the UI without polling.
4.  **Configure Edge:** User changes an intrusion zone. Frontend sends a `PUT` request to FastAPI (`/api/v1/devices/:id/settings`). FastAPI saves it and pushes the update to the edge device via SSE.
