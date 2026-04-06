# Deployment Guide

Sentinel is designed for seamless modern cloud deployment using fully managed services. This minimizes operations while keeping the application highly available and scalable.

## Recommended Architecture

*   **Database:** [Neon](https://neon.tech) (Serverless Postgres) or [Supabase](https://supabase.com).
*   **Cache:** [Upstash](https://upstash.com) (Serverless Redis) or Railway Redis.
*   **Backend & Worker:** [Render](https://render.com) or [Railway](https://railway.app).
*   **Frontend:** [Vercel](https://vercel.com) or [Netlify](https://netlify.com).

## Pre-requisites

You need accounts on your chosen platforms (e.g. Neon, Upstash, Render, Vercel) and the repository code pushed to a GitHub repository so these platforms can connect to it.

## Deployment Steps

Deploying Sentinel involves setting up the data layer, then deploying backend services, and finally deploying the frontend.

### 1. Database & Cache (Neon & Upstash)

1.  **PostgreSQL**: Create a new Postgres project on Neon. Copy the connection string.
2.  **Redis**: Create a Redis database on Upstash. Copy the connection string.

### 2. Backend API (Render)

1.  Create a **New Web Service** in Render.
2.  Connect your GitHub repository.
3.  Configure the settings:
    *   **Root Directory**: leave blank.
    *   **Environment**: Docker. Render will use `backend/Dockerfile`. Wait, Render needs to know which Dockerfile to use. To make this easy, set the Dockerfile Path to `backend/Dockerfile`.
    *   **Context Directory**: `.` (root of repo), so `backend/` and `worker/` are accessible if needed.
4.  Add the following Environment Variables:
    *   `DATABASE_URL`: Your Postgres connection string from Step 1.
    *   `REDIS_URL`: Your Redis connection string from Step 1.
    *   `DEBUG`: `false`
    *   `FRONTEND_URL`: Leave blank or set to `*` for now, update once Frontend is deployed.
5.  Deploy the backend. Keep note of the generated Render URL (e.g., `https://sentinel-api.onrender.com`).

### 3. Background Worker (Render)

1.  Create a **New Background Worker** in Render. 
2.  Connect the same repository.
3.  Configure the settings:
    *   **Environment**: Docker.
    *   **Dockerfile Path**: `worker/Dockerfile`
    *   **Context Directory**: `.` (root of the repo)
4.  Add the exact same environment variables as the Backend:
    *   `DATABASE_URL`, `REDIS_URL`, `DEBUG=false`.
5.  Deploy the worker. It will automatically run health checks and maintain the cache in the background.

### 4. Frontend (Vercel)

1.  Import your GitHub repo into Vercel.
2.  Configure the Project:
    *   **Framework Preset**: Vite
    *   **Root Directory**: `frontend`
    *   **Build Command**: `npm run build`
    *   **Output Directory**: `dist`
3.  Add the Environment Variable:
    *   `VITE_API_URL`: The backend URL you got from Render in Step 2, ending in `/api/v1` (e.g. `https://sentinel-api.onrender.com/api/v1`).
4.  Deploy the frontend. Note the Vercel URL.

### 5. Final Configuration 

1.  Go back to your Backend API settings in Render.
2.  Update the `FRONTEND_URL` environment variable to match your frontend URL (e.g., `https://sentinel-dashboard.vercel.app`).
3.  This ensures CORS is strictly allowed only from your frontend.

## Verification Checklist

- [ ] Visit frontend URL: Does the dashboard load without network errors?
- [ ] Are services shown as "Healthy" / updated recently? (Verifies DB read and backend REST API).
- [ ] Create a downtime/maintenance via the frontend toggle. Does it reflect instantly? (Verifies caching works).
- [ ] Wait 1-2 minutes: Do health check logs show updates under the hood? (Verifies worker is running properly).
