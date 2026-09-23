from __future__ import annotations
import json, os, shutil, time, traceback
from pathlib import Path
import requests
from dotenv import load_dotenv
from video_analyzer import analyze_video
from video_processor import render_plan

load_dotenv()
ROOT = Path(os.getenv("STORK_ROOT", ".")).resolve()
QUEUE = os.environ["QUEUE_BASE_URL"].rstrip("/")
TOKEN = os.environ["QUEUE_TOKEN"]
POLL = int(os.getenv("POLL_SECONDS", "15"))

def headers(): return {"Authorization": f"Bearer {TOKEN}"}

def download_source(job: dict, path: Path):
    if job.get("source_url"):
        with requests.get(job["source_url"], stream=True, timeout=300) as r:
            r.raise_for_status()
            with path.open("wb") as f:
                for chunk in r.iter_content(1024 * 1024): f.write(chunk)
    else:
        local = ROOT / "input" / job["source"]
        shutil.copy2(local, path)

def run_once():
    r = requests.post(f"{QUEUE}/v1/jobs/claim", headers=headers(), timeout=30)
    if r.status_code == 204: return False
    r.raise_for_status(); job = r.json(); job_id = job["job_id"]
    work = ROOT / "output" / job["release_id"]; work.mkdir(parents=True, exist_ok=True)
    source = work / job["source"]
    try:
        download_source(job, source)
        meta = analyze_video(source, work / "analysis")
        plan_path = work / "release_plan.json"
        plan_path.write_text(json.dumps(job["release_plan"], ensure_ascii=False, indent=2), encoding="utf-8")
        files = render_plan(source, job["release_plan"], work)
        payload = {"job_id": job_id, "status": "completed", "metadata": meta, "files": files}
        requests.post(f"{QUEUE}/v1/jobs/{job_id}/complete", json=payload, headers=headers(), timeout=30).raise_for_status()
    except Exception as exc:
        requests.post(f"{QUEUE}/v1/jobs/{job_id}/fail", json={"error": str(exc), "trace": traceback.format_exc()}, headers=headers(), timeout=30)
    return True

if __name__ == "__main__":
    while True:
        try: run_once()
        except Exception: traceback.print_exc()
        time.sleep(POLL)
