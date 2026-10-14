import sqlite3
import json
from pathlib import Path
from backend.config import DB_PATH
from backend.models import CustomerProfile, RequestLogEntry


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            prompt_preview TEXT,
            classification TEXT,
            selected_provider TEXT,
            selected_model TEXT,
            reason TEXT,
            latency_ms INTEGER,
            estimated_cost REAL,
            tokens_used INTEGER DEFAULT 0,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            ttft_ms INTEGER DEFAULT 0,
            status TEXT DEFAULT 'success',
            candidates_considered TEXT DEFAULT '[]',
            candidates_eliminated TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS global_models (
            model_name TEXT PRIMARY KEY,
            enabled INTEGER DEFAULT 1,
            description TEXT DEFAULT '',
            custom_config TEXT DEFAULT '{}'
        )
    """)
    # Add new columns if they don't exist (migration-safe)
    for col, typ, default in [
        ("input_tokens", "INTEGER", "0"),
        ("output_tokens", "INTEGER", "0"),
        ("ttft_ms", "INTEGER", "0"),
        ("status", "TEXT", "'success'"),
        ("candidates_considered", "TEXT", "'[]'"),
        ("candidates_eliminated", "TEXT", "'{}'"),
    ]:
        try:
            conn.execute(f"ALTER TABLE request_logs ADD COLUMN {col} {typ} DEFAULT {default}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

    # Seed default models if the table is empty
    seed_default_models()


# --- Customers ---

def save_customer(profile: CustomerProfile):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO customers (customer_id, data, created_at) VALUES (?, ?, ?)",
        (profile.customer_id, profile.model_dump_json(), profile.created_at),
    )
    conn.commit()
    conn.close()


def get_customer(customer_id: str) -> CustomerProfile | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT data FROM customers WHERE customer_id = ?", (customer_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return CustomerProfile.model_validate_json(row["data"])


def list_customers() -> list[CustomerProfile]:
    conn = get_connection()
    rows = conn.execute("SELECT data FROM customers ORDER BY created_at DESC").fetchall()
    conn.close()
    return [CustomerProfile.model_validate_json(row["data"]) for row in rows]


def delete_customer(customer_id: str) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


# --- Request Logs ---

def save_request_log(entry: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO request_logs
        (customer_id, timestamp, prompt_preview, classification, selected_provider,
         selected_model, reason, latency_ms, estimated_cost, tokens_used,
         input_tokens, output_tokens, ttft_ms, status,
         candidates_considered, candidates_eliminated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry["customer_id"],
            entry["timestamp"],
            entry["prompt_preview"],
            entry["classification"],
            entry["selected_provider"],
            entry["selected_model"],
            entry["reason"],
            entry["latency_ms"],
            entry["estimated_cost"],
            entry["tokens_used"],
            entry.get("input_tokens", 0),
            entry.get("output_tokens", 0),
            entry.get("ttft_ms", 0),
            entry.get("status", "success"),
            json.dumps(entry.get("candidates_considered", [])),
            json.dumps(entry.get("candidates_eliminated", {})),
        ),
    )
    conn.commit()
    conn.close()


def get_request_logs(customer_id: str | None = None, limit: int = 100) -> list[dict]:
    conn = get_connection()
    if customer_id:
        rows = conn.execute(
            "SELECT * FROM request_logs WHERE customer_id = ? ORDER BY timestamp DESC LIMIT ?",
            (customer_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        # Parse JSON fields
        for field in ("candidates_considered", "candidates_eliminated"):
            if field in d and isinstance(d[field], str):
                try:
                    d[field] = json.loads(d[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        results.append(d)
    return results


def get_customer_stats(customer_id: str) -> dict:
    conn = get_connection()
    raw_rows = conn.execute(
        "SELECT * FROM request_logs WHERE customer_id = ?", (customer_id,)
    ).fetchall()
    conn.close()
    rows = [dict(r) for r in raw_rows]

    if not rows:
        return {
            "total_requests": 0,
            "avg_latency_ms": 0,
            "p95_latency_ms": 0,
            "p99_latency_ms": 0,
            "total_cost": 0,
            "cost_savings_vs_premium": 0,
            "total_tokens": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "avg_ttft_ms": 0,
            "success_rate": 100,
            "model_distribution": {},
            "requests_by_tier": {},
            "provider_distribution": {},
            "cost_by_model": {},
            "latency_by_model": {},
            "hourly_requests": [],
        }

    total = len(rows)
    latencies = sorted([r["latency_ms"] for r in rows])
    total_latency = sum(latencies)
    total_cost = sum(r["estimated_cost"] for r in rows)
    total_tokens = sum(r["tokens_used"] for r in rows)
    total_input = sum(r.get("input_tokens") or 0 for r in rows)
    total_output = sum(r.get("output_tokens") or 0 for r in rows)
    ttfts = [r.get("ttft_ms") or 0 for r in rows if (r.get("ttft_ms") or 0) > 0]
    successes = sum(1 for r in rows if (r.get("status") or "success") == "success")

    # Cost if everything went to the most expensive enabled model (the "no routing" baseline)
    from backend.services.provider_registry import get_active_catalog, estimate_cost
    catalog = get_active_catalog()
    # Find the most expensive model by combined input+output cost
    premium_model = max(
        catalog.items(),
        key=lambda x: x[1].get("cost_per_m_input", 0) + x[1].get("cost_per_m_output", 0),
    )
    premium_info = premium_model[1]
    premium_total = sum(
        ((r.get("input_tokens") or r["tokens_used"] // 2) / 1_000_000) * premium_info.get("cost_per_m_input", 0) +
        ((r.get("output_tokens") or r["tokens_used"] // 2) / 1_000_000) * premium_info.get("cost_per_m_output", 0)
        for r in rows
    )

    model_dist: dict[str, int] = {}
    tier_dist: dict[str, int] = {}
    provider_dist: dict[str, int] = {}
    cost_by_model: dict[str, float] = {}
    latency_by_model: dict[str, list] = {}

    for r in rows:
        model = r["selected_model"]
        tier = r["classification"]
        provider = r["selected_provider"]
        model_dist[model] = model_dist.get(model, 0) + 1
        tier_dist[tier] = tier_dist.get(tier, 0) + 1
        provider_dist[provider] = provider_dist.get(provider, 0) + 1
        cost_by_model[model] = round(cost_by_model.get(model, 0) + r["estimated_cost"], 6)
        if model not in latency_by_model:
            latency_by_model[model] = []
        latency_by_model[model].append(r["latency_ms"])

    avg_latency_by_model = {
        m: round(sum(lats) / len(lats), 1) for m, lats in latency_by_model.items()
    }

    # Hourly request counts (last 48 hours)
    from datetime import datetime, timedelta, timezone
    hourly: dict[str, int] = {}
    for r in rows:
        try:
            ts = datetime.fromisoformat(r["timestamp"])
            hour_key = ts.strftime("%Y-%m-%d %H:00")
            hourly[hour_key] = hourly.get(hour_key, 0) + 1
        except (ValueError, TypeError):
            pass

    hourly_list = [{"hour": k, "count": v} for k, v in sorted(hourly.items())]

    p95_idx = min(int(total * 0.95), total - 1)
    p99_idx = min(int(total * 0.99), total - 1)

    return {
        "total_requests": total,
        "avg_latency_ms": round(total_latency / total, 1),
        "p95_latency_ms": latencies[p95_idx],
        "p99_latency_ms": latencies[p99_idx],
        "total_cost": round(total_cost, 6),
        "cost_savings_vs_premium": round(premium_total - total_cost, 6),
        "total_tokens": total_tokens,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "avg_ttft_ms": round(sum(ttfts) / len(ttfts), 1) if ttfts else 0,
        "success_rate": round((successes / total) * 100, 1),
        "model_distribution": model_dist,
        "requests_by_tier": tier_dist,
        "provider_distribution": provider_dist,
        "cost_by_model": cost_by_model,
        "latency_by_model": avg_latency_by_model,
        "hourly_requests": hourly_list,
    }


def get_global_stats() -> dict:
    conn = get_connection()
    raw_rows = conn.execute("SELECT * FROM request_logs ORDER BY timestamp DESC").fetchall()
    customer_rows = conn.execute("SELECT data FROM customers").fetchall()
    conn.close()
    rows = [dict(r) for r in raw_rows]

    total = len(rows)
    if total == 0:
        return {
            "total_requests": 0,
            "total_customers": len(customer_rows),
            "total_cost": 0,
            "cost_savings_vs_premium": 0,
            "avg_latency_ms": 0,
            "requests_today": 0,
            "cost_today": 0,
            "model_distribution": {},
            "provider_distribution": {},
            "customer_request_counts": {},
            "hourly_requests": [],
        }

    total_cost = sum(r["estimated_cost"] for r in rows)
    total_latency = sum(r["latency_ms"] for r in rows)

    from backend.services.provider_registry import get_active_catalog
    catalog = get_active_catalog()
    premium_model = max(
        catalog.items(),
        key=lambda x: x[1].get("cost_per_m_input", 0) + x[1].get("cost_per_m_output", 0),
    )
    premium_info = premium_model[1]
    premium_total = sum(
        ((r.get("input_tokens") or r["tokens_used"] // 2) / 1_000_000) * premium_info.get("cost_per_m_input", 0) +
        ((r.get("output_tokens") or r["tokens_used"] // 2) / 1_000_000) * premium_info.get("cost_per_m_output", 0)
        for r in rows
    )

    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_rows = [r for r in rows if r["timestamp"].startswith(today)]

    model_dist: dict[str, int] = {}
    provider_dist: dict[str, int] = {}
    customer_counts: dict[str, int] = {}
    hourly: dict[str, int] = {}

    for r in rows:
        model_dist[r["selected_model"]] = model_dist.get(r["selected_model"], 0) + 1
        provider_dist[r["selected_provider"]] = provider_dist.get(r["selected_provider"], 0) + 1
        customer_counts[r["customer_id"]] = customer_counts.get(r["customer_id"], 0) + 1
        try:
            ts = datetime.fromisoformat(r["timestamp"])
            hour_key = ts.strftime("%Y-%m-%d %H:00")
            hourly[hour_key] = hourly.get(hour_key, 0) + 1
        except (ValueError, TypeError):
            pass

    return {
        "total_requests": total,
        "total_customers": len(customer_rows),
        "total_cost": round(total_cost, 6),
        "cost_savings_vs_premium": round(premium_total - total_cost, 6),
        "avg_latency_ms": round(total_latency / total, 1),
        "requests_today": len(today_rows),
        "cost_today": round(sum(r["estimated_cost"] for r in today_rows), 6),
        "model_distribution": model_dist,
        "provider_distribution": provider_dist,
        "customer_request_counts": customer_counts,
        "hourly_requests": [{"hour": k, "count": v} for k, v in sorted(hourly.items())],
    }


# --- Global Model Registry ---

def get_global_models() -> list[dict]:
    """Return all models from DB with full metadata."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM global_models").fetchall()
    conn.close()

    if not rows:
        # Fallback to DEFAULT_MODELS if DB is empty
        from backend.services.provider_registry import DEFAULT_MODELS
        result = []
        for name, info in DEFAULT_MODELS.items():
            entry = {
                "model_name": name,
                "enabled": True,
                "description": info["description"],
                **info,
            }
            result.append(entry)
        return result

    result = []
    for r in rows:
        row_dict = dict(r)
        entry = {
            "model_name": row_dict["model_name"],
            "enabled": bool(row_dict["enabled"]),
            "description": row_dict["description"],
        }
        # Parse custom_config to get full metadata
        try:
            config = json.loads(row_dict.get("custom_config", "{}"))
            entry.update(config)
        except (json.JSONDecodeError, TypeError):
            pass
        result.append(entry)
    return result


def get_global_models_full() -> dict:
    """Return a dict keyed by model_name with full model metadata.
    Used by provider_registry.get_active_catalog().
    """
    conn = get_connection()
    rows = conn.execute("SELECT * FROM global_models").fetchall()
    conn.close()

    if not rows:
        return {}

    result = {}
    for r in rows:
        row_dict = dict(r)
        model_name = row_dict["model_name"]
        try:
            config = json.loads(row_dict.get("custom_config", "{}"))
        except (json.JSONDecodeError, TypeError):
            config = {}

        # Only include models that have full metadata in custom_config
        if config and "provider" in config:
            result[model_name] = config
            # Ensure enabled status is tracked
            if not row_dict["enabled"]:
                result[model_name]["_enabled"] = False

    return result


def add_global_model(model_data: dict):
    """Insert or replace a model with all its metadata stored as JSON in custom_config."""
    model_name = model_data["model_name"]
    description = model_data.get("description", "")

    # Store all metadata fields in custom_config
    config_fields = {
        "provider": model_data.get("provider", "unknown"),
        "openrouter_id": model_data.get("openrouter_id", model_name),
        "tier": model_data.get("tier", "medium"),
        "cost_per_m_input": model_data.get("cost_per_m_input", 1.0),
        "cost_per_m_output": model_data.get("cost_per_m_output", 5.0),
        "avg_latency_ms": model_data.get("avg_latency_ms", 500),
        "regions": model_data.get("regions", ["US"]),
        "max_context": model_data.get("max_context", 128000),
        "description": description,
    }

    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO global_models (model_name, enabled, description, custom_config)
        VALUES (?, ?, ?, ?)""",
        (model_name, 1, description, json.dumps(config_fields)),
    )
    conn.commit()
    conn.close()


def remove_global_model(model_name: str) -> bool:
    """Delete a model from the global_models table."""
    conn = get_connection()
    cursor = conn.execute("DELETE FROM global_models WHERE model_name = ?", (model_name,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def seed_default_models(default_models: dict | None = None):
    """If global_models table is empty, seed it from the DEFAULT_MODELS dict."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM global_models").fetchone()[0]
    conn.close()

    if count > 0:
        return

    # Lazy import to avoid circular dependency
    if default_models is None:
        from backend.services.provider_registry import DEFAULT_MODELS
        default_models = DEFAULT_MODELS

    for model_name, info in default_models.items():
        model_data = {"model_name": model_name, **info}
        add_global_model(model_data)


def update_global_model(model_name: str, enabled: bool, description: str = ""):
    conn = get_connection()
    # Check if model exists
    row = conn.execute("SELECT custom_config FROM global_models WHERE model_name = ?", (model_name,)).fetchone()
    if row:
        # Preserve existing custom_config, just update enabled and description
        custom_config = row["custom_config"]
        if description:
            try:
                config = json.loads(custom_config)
                config["description"] = description
                custom_config = json.dumps(config)
            except (json.JSONDecodeError, TypeError):
                pass
        conn.execute(
            """UPDATE global_models SET enabled = ?, description = ?, custom_config = ?
            WHERE model_name = ?""",
            (int(enabled), description, custom_config, model_name),
        )
    else:
        conn.execute(
            """INSERT INTO global_models (model_name, enabled, description, custom_config)
            VALUES (?, ?, ?, ?)""",
            (model_name, int(enabled), description, "{}"),
        )
    conn.commit()
    conn.close()


def get_enabled_models() -> list[str]:
    """Return list of enabled model names from DB."""
    conn = get_connection()
    rows = conn.execute("SELECT model_name, enabled FROM global_models").fetchall()
    conn.close()

    if not rows:
        # Fallback to DEFAULT_MODELS if DB is empty
        from backend.services.provider_registry import DEFAULT_MODELS
        return list(DEFAULT_MODELS.keys())

    return [r["model_name"] for r in rows if r["enabled"]]
