from __future__ import annotations
import json, os, shutil, time, traceback, logging
from pathlib import Path
import requests
import gdown
from dotenv import load_dotenv
from video_analyzer import analyze_video
from video_processor import render_plan

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

load_dotenv()

raw_root = os.getenv("STORK_ROOT", ".")
ROOT = Path(raw_root).expanduser().resolve()

QUEUE = os.environ["QUEUE_BASE_URL"].rstrip("/")
TOKEN = os.environ["QUEUE_TOKEN"]
POLL = int(os.getenv("POLL_SECONDS", "15"))

def headers(): 
    return {"Authorization": f"Bearer {TOKEN}"}

def download_source(job: dict, path: Path):
    if job.get("source_url"):
        logging.info(f"Stahuji zdrojový soubor z URL: {job['source_url']}")
        
        if "drive.google.com" in job["source_url"]:
            output_str = str(path)
            res = gdown.download(url=job["source_url"], output=output_str, quiet=False)
            if res is None or not path.exists() or path.stat().st_size == 0:
                raise RuntimeError(f"Stažení z Google Drive selhalo nebo stáhlo prázdný soubor.")
        else:
            session = requests.Session()
            with session.get(job["source_url"], stream=True, timeout=300) as r:
                r.raise_for_status()
                with path.open("wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        if chunk:
                            f.write(chunk)
    else:
        local = ROOT / "input" / job["source"]
        logging.warning(f"URL nenalezeno. Hledám lokální soubor: {local}")
        if not local.exists():
            raise FileNotFoundError(f"Lokální soubor {local} neexistuje a source_url chybí.")
        shutil.copy2(local, path)

def run_once():
    r = requests.post(f"{QUEUE}/v1/jobs/claim", headers=headers(), timeout=30)
    if r.status_code == 204: 
        return False
        
    r.raise_for_status()
    job = r.json()
    job_id = job.get("job_id", "unknown")
    
    if job.get("type") and job.get("type") != "video_processing":
        logging.warning(f"Ignoruji úlohu {job_id}: nesprávný typ '{job.get('type')}'.")
        requests.post(f"{QUEUE}/v1/jobs/{job_id}/fail", json={"error": f"Nepodporovaný typ úlohy: {job.get('type')}"}, headers=headers(), timeout=30)
        return True

    logging.info(f"Přijata úloha: {job_id} pro release: {job.get('release_id')}")
    
    work = ROOT / "output" / job["release_id"]
    work.mkdir(parents=True, exist_ok=True)
    source = work / job["source"]
    
    try:
        download_source(job, source)
        
        logging.info(f"Analyzuji video: {source.name}")
        meta = analyze_video(source, work / "analysis")
        
        logging.info("Ukládám plán vydání...")
        plan_path = work / "release_plan.json"
        plan_path.write_text(json.dumps(job["release_plan"], ensure_ascii=False, indent=2), encoding="utf-8")
        
        logging.info("Spouštím renderování klipů...")
        files = render_plan(source, job["release_plan"], work)
        
        payload = {"job_id": job_id, "status": "completed", "metadata": meta, "files": files}
        requests.post(f"{QUEUE}/v1/jobs/{job_id}/complete", json=payload, headers=headers(), timeout=30).raise_for_status()
        logging.info(f"Úloha {job_id} úspěšně dokončena.")
        
    except Exception as exc:
        logging.error(f"Chyba při zpracování úlohy {job_id}: {exc}")
        requests.post(f"{QUEUE}/v1/jobs/{job_id}/fail", json={"error": str(exc), "trace": traceback.format_exc()}, headers=headers(), timeout=30)
        
    return True

if __name__ == "__main__":
    logging.info(f"Worker spuštěn. Sleduji frontu na: {QUEUE}")
    while True:
        try: 
            run_once()
        except requests.exceptions.RequestException as e:
            logging.error(f"Chyba připojení k frontě: {e}")
        except Exception: 
            logging.error("Neočekávaná chyba workeru:")
            traceback.print_exc()
        time.sleep(POLL)
