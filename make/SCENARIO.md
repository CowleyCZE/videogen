# Make scénář STORK COMMAND V1

## Scénář A — spuštění release

1. **Google Drive > Watch files in a folder** — sleduj `COWLEY_CONTENT/INPUT`; filtruj pouze `.mp4`, stav `new` a zpracovávej po jednom souboru.
2. **Google Drive > Download a file** — stáhni video pouze pokud ho Make potřebuje pro upload/archivaci; notebook může použít podepsanou URL nebo kopii v INPUT.
3. **Tools > Set variables** — `release_id`, `song`, `release_day`, `spotify_url`, `available_platforms`.
4. **HTTP > Make a request (Groq)** — `POST https://api.groq.com/openai/v1/chat/completions`, `Authorization: Bearer {{GROQ_API_KEY}}`, JSON body podle `make/groq-request.json`; model musí podporovat Structured Outputs. Vlož metadata, timestampovaný přepis a pravidla z promptu.
5. **JSON > Parse JSON** — schema `schemas/release_plan.json`.
6. **HTTP > Make a request (fronta)** — `POST {{QUEUE_BASE_URL}}/v1/jobs`, Bearer `QUEUE_TOKEN`, body podle `make/queue-job.json`. Neposílej video přes Make; pošli `source`/`source_url` a celý `release_plan`.
7. **Google Drive > Create a folder** — `OUTPUT/{{release_id}}`.
8. **Google Drive > Create a file** — ulož `release_plan.json` do výstupní složky.
9. **Google Drive > Update a file** — přejmenuj zdroj na `processed/{{release_id}}__...` nebo přesuň do `ARCHIVE`, aby se nespustil znovu.
10. **Slack/Email volitelně** — potvrď `job_id` a plán; neposílej TikTok/Instagram automaticky ve V1.

## Scénář B — dokončení výroby

1. **Webhooks > Custom webhook** — endpoint přijme callback z fronty jen pokud fronta umí callback; jinak použij `Tools > Sleep` + `HTTP GET /v1/jobs/{job_id}` v samostatném pollovacím scénáři.
2. **Google Drive > Upload a file** — nahraj hotové MP4 do `OUTPUT/{{release_id}}/{platform}`.
3. **YouTube > Upload a video** — hlavní video publikuj až po ručním schválení; Shorts lze nejdřív uložit jako draft/naplánovat.
4. **Instagram for Business > Create Reel** — vyžaduje profesionální účet, oprávnění a veřejně dostupné médium podle aktuálního konektoru.
5. **TikTok** — V1 pouze připrav draft/manual upload. Přímé API publish zapni až po ověření aplikace, oprávnění a pravidel účtu.

## Ochrany

- Filtruj `job_id` jako unikátní klíč, aby opakovaný Drive trigger nevytvořil druhou úlohu.
- Nastav retry HTTP na 3 pokusy s exponenciálním odstupem; při chybě ponech soubor v INPUT a pošli alert.
- Před veřejným publikováním nech stav `approval_required=true` nebo použij samostatný schvalovací scénář.
- API klíče ulož do Make Connections/Secrets, ne do názvu souboru ani do logu.
