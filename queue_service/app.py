from __future__ import annotations
import os, secrets, sqlite3, json
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = os.getenv("QUEUE_DB", "queue.sqlite3")
TOKEN = os.environ["QUEUE_TOKEN"]

def auth():
    return secrets.compare_digest(request.headers.get("Authorization", ""), f"Bearer {TOKEN}")

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS jobs (job_id TEXT PRIMARY KEY, status TEXT NOT NULL, payload TEXT NOT NULL, result TEXT, error TEXT)")
    c.commit(); return c

@app.post("/v1/jobs")
def enqueue():
    if not auth(): return jsonify(error="unauthorized"), 401
    data = request.get_json(force=True)
    
    # VALIDACE: Zajištění správného formátu od Make
    if not data.get("release_plan"):
        return jsonify(error="missing_release_plan"), 400
    if not data.get("source") and not data.get("source_url"):
         return jsonify(error="missing_source"), 400
         
    job_id = data.get("job_id") or secrets.token_hex(12)
    # Pro jistotu vložíme job_id i do vnitřního payloadu
    data["job_id"] = job_id 
    
    c = db()
    c.execute("INSERT OR IGNORE INTO jobs VALUES (?, 'queued', ?, NULL, NULL)", (job_id, json.dumps(data)))
    c.commit()
    return jsonify(job_id=job_id, status="queued"), 202

@app.post("/v1/jobs/claim")
def claim():
    if not auth(): return jsonify(error="unauthorized"), 401
    c = db()
    # Můžeme přidat filtraci pro konkrétní typy úloh, pokud je workerů více
    row = c.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY rowid LIMIT 1").fetchone()
    if not row: return "", 204
    
    c.execute("UPDATE jobs SET status='processing' WHERE job_id=?", (row["job_id"],))
    c.commit()
    
    payload = json.loads(row["payload"])
    payload.update(job_id=row["job_id"])
    return jsonify(payload)

def finish(job_id, status):
    if not auth(): return jsonify(error="unauthorized"), 401
    data = request.get_json(force=True)
    c = db()
    c.execute("UPDATE jobs SET status=?, result=?, error=? WHERE job_id=?", (status, json.dumps(data), data.get("error"), job_id))
    c.commit()
    return jsonify(job_id=job_id, status=status)

@app.post("/v1/jobs/<job_id>/complete")
def complete(job_id): return finish(job_id, "completed")

@app.post("/v1/jobs/<job_id>/fail")
def fail(job_id): return finish(job_id, "failed")

@app.get("/v1/jobs/<job_id>")
def status(job_id):
    if not auth(): return jsonify(error="unauthorized"), 401
    row = db().execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
    if not row: return jsonify(error="not_found"), 404
    return jsonify(job_id=job_id, status=row["status"], result=json.loads(row["result"]) if row["result"] else None, error=row["error"])

@app.get("/health")
def health(): return jsonify(ok=True)

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
