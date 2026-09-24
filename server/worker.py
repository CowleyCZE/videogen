import os
import sys
import time
import json
import logging
import requests
import gdown
from pathlib import Path
from moviepy import VideoFileClip

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

QUEUE_URL = os.getenv("QUEUE_URL", "https://stork-command-queue.onrender.com")
QUEUE_TOKEN = os.getenv("QUEUE_TOKEN", "hheesslloo3206")
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

HEADERS = {
    "Authorization": f"Bearer {QUEUE_TOKEN}",
    "Content-Type": "application/json"
}

PLATFORM_CONFIGS = {
    "tiktok": {"resolution": (1080, 1920), "aspect_ratio": "9:16"},
    "instagram": {"resolution": (1080, 1920), "aspect_ratio": "9:16"},
    "youtube": {"resolution": (1080, 1920), "aspect_ratio": "9:16"},
    "facebook": {"resolution": (1080, 1920), "aspect_ratio": "9:16"},
    "default": {"resolution": (1080, 1920), "aspect_ratio": "9:16"}
}

def claim_job():
    url = f"{QUEUE_URL}/v1/jobs/claim"
    try:
        response = requests.post(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return None
    except Exception as e:
        logging.error(f"Chyba při komunikaci s frontou: {e}")
    return None

def fail_job(job_id, error_message):
    url = f"{QUEUE_URL}/v1/jobs/{job_id}/fail"
    payload = {"error": str(error_message)}
    try:
        requests.post(url, headers=HEADERS, json=payload, timeout=15)
    except Exception as e:
        logging.error(f"Chyba při odesílání selhání úlohy: {e}")

def complete_job(job_id, result_data):
    url = f"{QUEUE_URL}/v1/jobs/{job_id}/complete"
    try:
        requests.post(url, headers=HEADERS, json=result_data, timeout=15)
    except Exception as e:
        logging.error(f"Chyba při dokončování úlohy: {e}")

def process_job(job):
    job_id = job.get("job_id") or job.get("id")
    release_id = job.get("release_id", "default_release")
    source_url = job.get("source_url")
    release_plan = job.get("release_plan", {})

    logging.info(f"Přijata úloha: {job_id} pro release: {release_id}")

    release_dir = OUTPUT_DIR / release_id
    release_dir.mkdir(parents=True, exist_ok=True)

    source_path = release_dir / f"{release_id}.mp4"

    logging.info(f"Stahuji zdrojový soubor z URL: {source_url}")
    gdown.download(source_url, str(source_path), quiet=False)

    if not source_path.exists():
        raise FileNotFoundError(f"Soubor nebyl stažen: {source_path}")

    logging.info(f"Analyzuji video: {source_path.name}")
    
    logging.info("Ukládám plán vydání...")
    plan_path = release_dir / "release_plan.json"
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(release_plan, f, ensure_ascii=False, indent=2)

    logging.info("Spouštím renderování klipů...")
    clips_data = release_plan.get("clips", [])

    if clips_data:
        video = VideoFileClip(str(source_path))
        for clip_info in clips_data:
            clip_id = clip_info.get("id", "clip")
            start = clip_info.get("start", 0)
            end = clip_info.get("end", video.duration)
            
            raw_platforms = clip_info.get("platforms", [])
            if isinstance(raw_platforms, str):
                raw_platforms = [raw_platforms]
            
            platforms = [p.lower() for p in raw_platforms] if raw_platforms else ["default"]

            for platform in platforms:
                config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["default"])
                target_w, target_h = config["resolution"]

                # MoviePy v2.x kompatibilní metody:
                # 1. subclip -> subclipped
                # 2. resize -> resized
                # 3. crop -> cropped
                subclip = video.subclipped(start, min(end, video.duration))

                subclip_resized = subclip.resized(height=target_h)
                if subclip_resized.w > target_w:
                    crop_x1 = (subclip_resized.w - target_w) / 2
                    subclip_final = subclip_resized.cropped(x1=crop_x1, width=target_w)
                else:
                    subclip_final = subclip_resized

                out_clip_path = release_dir / f"{clip_id}_{platform}.mp4"
                subclip_final.write_videofile(
                    str(out_clip_path),
                    codec="libx264",
                    audio_codec="aac",
                    logger=None
                )
        video.close()

    logging.info(f"Úloha {job_id} byla úspěšně dokončena.")
    complete_job(job_id, {"status": "success", "release_id": release_id})

def main():
    logging.info(f"Worker spuštěn. Sleduji frontu na: {QUEUE_URL}")
    while True:
        try:
            job = claim_job()
            if job:
                job_id = job.get("job_id") or job.get("id")
                try:
                    process_job(job)
                except Exception as e:
                    logging.error(f"Chyba při zpracování úlohy {job_id}: {e}")
                    fail_job(job_id, str(e))
            else:
                time.sleep(15)
        except KeyboardInterrupt:
            logging.info("Worker byl ukončen uživatelem.")
            sys.exit(0)
        except Exception as e:
            logging.error(f"Neočekávaná chyba ve workeru: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
