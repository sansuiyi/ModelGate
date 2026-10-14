#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║       ModelGate — AI Control Plane           ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# Seed demo data if DB doesn't exist
if [ ! -f /app/backend/data/controlplane.db ]; then
    echo "[setup] Seeding demo data..."
    cd /app && python scripts/seed_data.py 2>/dev/null || echo "[setup] No seed script or seeding skipped"
    echo "[setup] Done"
fi

echo "[start] Starting backend on port 8000..."
cd /app
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
for i in $(seq 1 30); do
    if curl -s -o /dev/null http://localhost:8000/health 2>/dev/null; then
        echo "[start] Backend is ready"
        break
    fi
    sleep 1
done

echo "[start] Starting frontend on port 3000..."
cd /app/frontend
npx next start --hostname 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

sleep 2
echo ""
echo "  ModelGate is running!"
echo "  Dashboard:  http://localhost:3000"
echo "  API:        http://localhost:8000"
echo "  API Docs:   http://localhost:8000/docs"
echo ""

# Graceful shutdown
cleanup() {
    echo "[shutdown] Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "[shutdown] All services stopped"
    exit 0
}

trap cleanup INT TERM
wait
