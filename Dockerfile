# =============================================================
# ModelGate — Contract-Aware AI Control Plane
# Multi-stage Docker build: frontend + backend in one image
# =============================================================

# ── Stage 1: Build the Next.js frontend ─────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Runtime — Python backend + built frontend ──────
FROM python:3.12-slim AS runtime

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source
COPY backend/ /app/backend/

# Copy frontend build + node_modules (needed for next start)
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder /app/frontend/public /app/frontend/public
COPY --from=frontend-builder /app/frontend/package.json /app/frontend/package.json
COPY --from=frontend-builder /app/frontend/node_modules /app/frontend/node_modules
COPY --from=frontend-builder /app/frontend/next.config.ts /app/frontend/next.config.ts

# Copy seed data and scripts
COPY scripts/ /app/scripts/
COPY docs/ /app/docs/

# Create data directory
RUN mkdir -p /app/backend/data

# Entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose ports: backend (8000) + frontend (3000)
EXPOSE 8000 3000

ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

ENTRYPOINT ["/app/docker-entrypoint.sh"]
