# STORK COMMAND V1

STORK COMMAND V1 je hybridní výrobní linka pro hudební videa. Make řídí workflow, Groq vytváří validovaný release plán a notebook s Pythonem a FFmpeg vyrábí vertikální klipy. Notebook není vystavený veřejnému internetu: pouze aktivně vyzvedává úlohy z HTTPS fronty.

## Co je součástí

| Část | Účel |
|---|---|
| `prompts/stork_command.txt` | systémová pravidla pro Groq |
| `schemas/release_plan.json` | kontrakt mezi Groq, Make a workerem |
| `server/video_analyzer.py` | FFprobe metadata a audio příprava |
| `server/video_processor.py` | render 9:16 / 1080×1920 přes FFmpeg |
| `server/worker.py` | bezpečné vyzvednutí, zpracování a callback |
| `queue_service/app.py` | malá fronta s SQLite pro Make ↔ notebook |
| `make/SCENARIO.md` | nastavení Make modul po modulu |

## Předpoklady

- Windows/macOS/Linux notebook, který může běžet během zpracování;
- Python 3.11+ a FFmpeg s `ffmpeg` i `ffprobe` v PATH;
- Google Drive a Make účet;
- Groq API key pro generování plánů/transkripci;
- veřejně dostupná HTTPS instance `queue_service` (např. vlastní server nebo hosting); notebook ji pouze polluje.

## Instalace notebooku

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Vyplň `.env`, hlavně `QUEUE_BASE_URL`, `QUEUE_TOKEN` a `STORK_ROOT`. Tajné klíče nikdy necommituj.

Spuštění workeru:

```bash
cd server
python worker.py
```

Worker je idempotentní podle `job_id`. Při chybě se úloha označí jako failed; zdroj zůstává k dispozici pro opakování.

## Spuštění fronty

```bash
cd queue_service
export QUEUE_TOKEN='silne-tajne-heslo'
python app.py
```

Pro produkci použij HTTPS reverse proxy a autentizaci na úrovni hostingu. Neprovozuj Flask development server přímo do internetu.

## V1 publikační politika

V první verzi se automaticky vyrábějí soubory, ale veřejné publikování je schvalovací krok. TikTok je nastaven na draft/manual režim. Do TikTok videa se nevkládá „Sleduj na YouTube“ ani jiný watermark; CTA patří do popisku. Přímé publikování se zapíná až po ověření účtu, oprávnění a aktuálních pravidel platformy.

## První test

1. Vlož krátké testovací MP4 do `input/`.
2. V Make spusť scénář ručně s názvem skladby a datem vydání.
3. Ověř, že Groq vrací JSON validní proti `schemas/release_plan.json`.
4. Ověř, že fronta ukáže `queued`, worker `processing` a následně `completed`.
5. Zkontroluj `output/<release_id>/shorts`, `reels` a `tiktok`.
6. Teprve potom připoj upload/publikaci v Make.

## Náklady a volby architektury

| Přístup | Trade-off | Náklady | Složitost |
|---|---|---:|---:|
| **Doporučená V1: Make + Groq + notebook + HTTPS fronta** | levné, notebook musí být online; Make zůstává orchestrátor | Make/Groq dle tarifu a použití | střední |
| Jednodušší: vše ručně na notebooku, Make jen spustí job | méně integrací, více ručních kroků a horší monitoring | nejnižší | nízká |
| Plně cloudová výrobní linka | notebook nemusí běžet, ale video processing a úložiště jsou dražší a složitější | vyšší | vysoká |

## Budoucí V2

Doplnit transkripci s timestampy, preview dashboard, retry/backoff, YouTube/Instagram publish po schválení, statistiky a následnou optimalizaci plánů. TikTok direct publish držet odděleně od V1.
