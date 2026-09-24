# STORK COMMAND V1: úplný návod pro Linux krok za krokem

Tento návod je napsaný pro začátečníka, který používá notebook s Ubuntu Linuxem 24.04. Návod používá jednu konkrétní cestu:

- **Google Drive** bude obsahovat vstupní videa.
- **Make.com** bude spouštět workflow.
- **Groq** bude vytvářet přepis a marketingový plán.
- **GitHub** bude ukládat kód fronty.
- **Render** bude provozovat zabezpečenou HTTPS frontu.
- **Notebook s Ubuntu** bude pravidelně vyzvedávat úlohy a vyrábět videa přes FFmpeg.
- **YouTube, Instagram a TikTok** budou v první verzi použity až po ruční kontrole hotových souborů.

V tomto návodu nepřipojujeme automatické veřejné publikování. Nejprve ověříme výrobu souborů. Toto je bezpečnější první test a zabrání zveřejnění chybného videa.

> **Co budeš na konci umět:** vložíš MP4 do Google Drive, spustíš Make scénář, Groq vytvoří plán, notebook stáhne úlohu z fronty a v adresáři `output` vytvoří vertikální videa.

---

## 1. Co si připrav před začátkem

Připrav si jeden e-mail, který použiješ pro všechny účty. Připrav si také název umělce, například `Cowley Stork`, a název testovací skladby.

Vytvoř si tyto účty:

1. Google účet pro Google Drive a YouTube.
2. Make účet na [make.com](https://www.make.com/).
3. Groq účet na [console.groq.com](https://console.groq.com/).
4. GitHub účet na [github.com](https://github.com/).
5. Render účet na [render.com](https://render.com/).
6. Instagram účet, který později převedeš na profesionální účet.
7. TikTok účet.

Během tohoto návodu si připrav heslo fronty. Použij přesně tento formát, ale vytvoř vlastní hodnotu:

```text
StorkQueue-2026-SEM-VLOZ-VLASTNI-DLOUHE-HESLO
```

Heslo si ulož do správce hesel. Do veřejného chatu ho neposílej.

---

## 2. Instalace programů na Ubuntu

### 2.1 Otevření Terminálu

Stiskni na klávesnici současně `Ctrl` + `Alt` + `T`. Otevře se okno s názvem **Terminal**.

Každý příkaz v tomto návodu vlož do Terminálu a potvrď klávesou `Enter`. Když Linux požádá o heslo, napiš heslo ke svému uživatelskému účtu. Při psaní hesla se na obrazovce nezobrazují znaky. Po napsání hesla stiskni `Enter`.

### 2.2 Instalace Pythonu, FFmpeg, Git a nástrojů

Vlož tento celý příkaz:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip ffmpeg git curl unzip
```

Po dokončení ověř instalaci:

```bash
python3 --version
ffmpeg -version | head -n 1
ffprobe -version | head -n 1
git --version
```

Musíš vidět verzi Pythonu, FFmpeg, FFprobe a Gitu. Když se zobrazí všechny čtyři verze, instalace je hotová.

### 2.3 Stažení balíčku STORK COMMAND

Stáhni soubor [stork_command_v1.zip](/home/ubuntu/CowleyStorkAutomation/stork_command_v1.zip) do složky `Stažené`.

V Terminálu spusť:

```bash
mkdir -p "$HOME/STORK_COMMAND"
unzip "$HOME/Stažené/stork_command_v1.zip" -d "$HOME/STORK_COMMAND"
cd "$HOME/STORK_COMMAND"
pwd
```

Terminál musí vypsat:

```text
/home/TVE_UZIVATELSKE_JMENO/STORK_COMMAND
```

Zkontroluj obsah:

```bash
ls
```

Musíš vidět soubory `README.md`, `.env.example`, `requirements.txt`, složky `server`, `queue_service`, `make`, `prompts` a `schemas`.

---

## 3. Vytvoření Python prostředí a konfigurace notebooku

V Terminálu zůstaneš ve složce projektu. Spusť:

```bash
cd "$HOME/STORK_COMMAND"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Na začátku řádku Terminálu se objeví `(.venv)`. To znamená, že používáš správné prostředí.

Vytvoř konfigurační soubor:

```bash
cp .env.example .env
nano .env
```

Otevře se textový editor. Smaž jeho obsah a vlož tento blok. Nahraď pouze hodnotu `QUEUE_TOKEN` vlastním heslem fronty. URL fronty doplníš po nasazení na Renderu.

```dotenv
STORK_ROOT=/home/TVE_UZIVATELSKE_JMENO/STORK_COMMAND
POLL_SECONDS=15
WORKER_TOKEN=change-me
MAX_CLIP_SECONDS=60
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
GROQ_TRANSCRIPTION_MODEL=whisper-large-v3-turbo
QUEUE_BASE_URL=https://STORK-QUEUE-URL.onrender.com
QUEUE_TOKEN=SEM_VLOZ_HESLO_FRONTY
TIKTOK_MODE=draft
```

V řádku `STORK_ROOT` nahraď `TVE_UZIVATELSKE_JMENO` jménem, které zobrazil příkaz `pwd`.

V řádku `QUEUE_BASE_URL` zatím ponech text `https://STORK-QUEUE-URL.onrender.com`. Po nasazení Renderu se sem vrátíš.

Ulož soubor takto:

1. Stiskni `Ctrl` + `O`.
2. Stiskni `Enter`.
3. Stiskni `Ctrl` + `X`.

Ověř, že soubor existuje:

```bash
ls -la .env
```

---

## 4. Vytvoření Groq API klíče

1. Otevři [console.groq.com](https://console.groq.com/).
2. Klikni na **Sign in**.
3. Přihlas se.
4. V levém menu klikni na **API Keys**.
5. Klikni na **Create API Key**.
6. Do pole **Name** napiš `stork-command-v1`.
7. Klikni na **Submit**.
8. Zkopíruj zobrazený klíč.
9. V Terminálu otevři konfiguraci:

```bash
cd "$HOME/STORK_COMMAND"
nano .env
```

10. Za `GROQ_API_KEY=` vlož klíč bez mezer.
11. Soubor ulož pomocí `Ctrl` + `O`, `Enter`, `Ctrl` + `X`.

API klíč je tajný. Nevkládej ho do Make názvu scénáře, do GitHubu ani do textu zprávy.

Pro plánování používáme model `openai/gpt-oss-20b`, který podle dokumentace Groq podporuje Strict Structured Outputs. Pro přepis používáme `whisper-large-v3-turbo`.[1] [2]

---

## 5. Nasazení HTTPS fronty na Render

Fronta přijímá úlohy z Make a notebook si je vyzvedává. Notebook proto nemusí mít veřejnou IP adresu.

### 5.1 Vytvoření GitHub repozitáře

1. Otevři [github.com/new](https://github.com/new).
2. Do pole **Repository name** napiš `stork-command-v1`.
3. Vyber **Private**.
4. Nezaškrtávej **Add a README file**.
5. Klikni na **Create repository**.
6. Na stránce nového repozitáře zkopíruj adresu HTTPS, která začíná `https://github.com/`.

V Terminálu spusť tyto příkazy. V posledním příkazu nahraď adresu textem, který jsi zkopíroval z GitHubu.

```bash
cd "$HOME/STORK_COMMAND"
git init
git add README.md .env.example requirements.txt Procfile render.yaml server queue_service prompts schemas make
 git commit -m "Initial STORK COMMAND V1"
git branch -M main
git remote add origin https://github.com/TVUJ_GITHUB_UCET/stork-command-v1.git
git push -u origin main
```

Při `git push` GitHub otevře přihlášení. Zadej své GitHub uživatelské jméno. Pro heslo použij GitHub Personal Access Token, ne běžné heslo.

### 5.2 Vytvoření GitHub Personal Access Token

1. Otevři [github.com/settings/tokens](https://github.com/settings/tokens).
2. Klikni na **Generate new token**.
3. Klikni na **Generate new token (classic)**.
4. Do pole **Note** napiš `stork-command-upload`.
5. Nastav **Expiration** na `90 days`.
6. Zaškrtni oprávnění `repo`.
7. Klikni na **Generate token**.
8. Token ihned zkopíruj.
9. Při dotazu na heslo v Terminálu vlož tento token.

### 5.3 Vytvoření Render Web Service

1. Otevři [dashboard.render.com](https://dashboard.render.com/).
2. Klikni na **New +**.
3. Vyber **Web Service**.
4. Klikni na **Build and deploy from a Git repository**.
5. Klikni na **Connect account** u GitHubu.
6. Povol přístup k repozitáři `stork-command-v1`.
7. Vyber repozitář `stork-command-v1`.
8. Do pole **Name** napiš `stork-command-queue`.
9. V poli **Language** vyber `Python 3`.
10. V poli **Branch** vyber `main`.
11. Do pole **Build Command** napiš:

```text
pip install -r requirements.txt
```

12. Do pole **Start Command** napiš:

```text
gunicorn --chdir queue_service app:app
```

13. V poli **Instance Type** vyber placenou instanci, která umožňuje persistent disk.
14. V části **Advanced** klikni na **Add Disk**.
15. Do pole **Name** napiš `stork-queue-data`.
16. Do pole **Mount Path** napiš `/var/data`.
17. Do pole **Size** napiš `1` GB.
18. V části **Environment Variables** klikni na **Add Environment Variable**.
19. Do pole **Key** napiš `QUEUE_TOKEN`.
20. Do pole **Value** vlož stejné heslo, které jsi vložil do `.env`.
21. Klikni na **Add Environment Variable**.
22. Do pole **Key** napiš `QUEUE_DB`.
23. Do pole **Value** napiš `/var/data/queue.sqlite3`.
24. Klikni na **Create Web Service**.

Po dokončení deploymentu Render zobrazí adresu ve tvaru:

```text
https://stork-command-queue.onrender.com
```

Zkopíruj tuto adresu. V Terminálu otevři `.env`:

```bash
cd "$HOME/STORK_COMMAND"
nano .env
```

Nahraď celý řádek `QUEUE_BASE_URL=` touto adresou. Za adresu nepřidávej lomítko. Ulož soubor.

Ověř frontu:

```bash
curl https://stork-command-queue.onrender.com/health
```

Musíš dostat:

```json
{"ok":true}
```

---

## 6. První test fronty bez Make

Tento test ověří, že Render a notebook spolu komunikují.

V Terminálu spusť:

```bash
cd "$HOME/STORK_COMMAND"
source .venv/bin/activate
python smoke_test.py
```

Musíš vidět:

```text
schema-ok queue-lifecycle-ok
```

Tento test používá lokální testovací databázi. Neodesílá žádné video do Renderu.

---

## 7. Vytvoření složek v Google Drive

1. Otevři [drive.google.com](https://drive.google.com/).
2. Klikni na **Nový**.
3. Klikni na **Nová složka**.
4. Napiš `COWLEY_CONTENT`.
5. Otevři složku `COWLEY_CONTENT`.
6. Vytvoř složku `INPUT`.
7. Vytvoř složku `OUTPUT`.
8. Vytvoř složku `ARCHIVE`.
9. Vytvoř složku `DATA`.
10. Otevři `DATA` a vytvoř textový soubor `release-settings.txt`.

Do `release-settings.txt` vlož:

```text
artist=Cowley Stork
spotify_url=https://open.spotify.com/artist/3dFUhelmNR3kaxu0S54ZMu
available_platforms=youtube,instagram,tiktok
language=cs
```

Soubor ulož. Do `INPUT` vlož testovací MP4. Použij video dlouhé alespoň 20 sekund. Pojmenuj ho:

```text
Mosty_mezi_nami.mp4
```

---

## 8. Připojení Google Drive v Make

1. Otevři [make.com](https://www.make.com/).
2. Klikni na **Log in**.
3. Přihlas se.
4. Klikni na **Scenarios**.
5. Klikni na **Create a new scenario**.
6. Klikni na velké tlačítko `+`.
7. Do vyhledávání napiš `Google Drive`.
8. Vyber **Watch Files in a Folder**.
9. Klikni na **Add** u připojení Google Drive.
10. Přihlas se stejným Google účtem, ve kterém je složka `COWLEY_CONTENT`.
11. V poli **Choose a Drive** vyber **My Drive**.
12. V poli **Folder** vyber `COWLEY_CONTENT/INPUT`.
13. V poli **Limit** napiš `1`.
14. Klikni na **Save**.

Tento modul spouští scénář po nalezení nového souboru v INPUT.

---

## 9. Přidání stažení videa

1. Klikni na `+` vpravo od Google Drive modulu.
2. Vyhledej `Google Drive`.
3. Vyber **Download a File**.
4. V poli **File ID** klikni do pole.
5. Z nabídky vyber hodnotu **ID** z prvního modulu.
6. Klikni na **Save**.

Make nyní stáhne video do paměti scénáře. Toto video se použije jako příloha pro transkripci.

---

## 10. Přidání Groq transkripce

1. Klikni na `+` vpravo od modulu **Download a File**.
2. Vyhledej `HTTP`.
3. Vyber **Make a request**.
4. Do pole **URL** vlož:

```text
https://api.groq.com/openai/v1/audio/transcriptions
```

5. V poli **Method** vyber `POST`.
6. V části **Headers** klikni na **Add item**.
7. Do pole **Name** napiš `Authorization`.
8. Do pole **Value** napiš `Bearer TVUJ_GROQ_API_KLIC` a nahraď `TVUJ_GROQ_API_KLIC` skutečným Groq klíčem.
9. V poli **Body type** vyber `multipart/form-data`.
10. V části **Body fields** přidej textové pole:

```text
Name: model
Value: whisper-large-v3-turbo
```

11. Přidej textové pole:

```text
Name: language
Value: cs
```

12. Přidej textové pole:

```text
Name: response_format
Value: verbose_json
```

13. Přidej textové pole:

```text
Name: timestamp_granularities[]
Value: segment
```

14. Přidej souborové pole:

```text
Name: file
```

15. Do hodnoty souborového pole namapuj **Data** z modulu **Download a File**.
16. Klikni na **Save**.

Klikni na **Run once** a vlož testovací video do `INPUT`. Po doběhnutí otevři výsledek HTTP modulu. Musí obsahovat pole `text` a pole `segments`.

---

## 11. Přidání Groq release plánu

1. Klikni na `+` vpravo od transkripčního HTTP modulu.
2. Vyber **HTTP > Make a request**.
3. Do **URL** vlož:

```text
https://api.groq.com/openai/v1/chat/completions
```

4. V poli **Method** vyber `POST`.
5. Přidej header:

```text
Name: Authorization
Value: Bearer TVUJ_GROQ_API_KLIC
```

6. Přidej header:

```text
Name: Content-Type
Value: application/json
```

7. V poli **Body type** vyber `Raw`.
8. V poli **Content type** vyber `application/json`.
9. Vlož tento JSON. Texty uvnitř dvojitých hranatých závorek nahraď namapovanými hodnotami z předchozích modulů.

```json
{
  "model": "openai/gpt-oss-20b",
  "temperature": 0.2,
  "messages": [
    {
      "role": "system",
      "content": "Jsi STORK COMMAND. Vrať pouze JSON podle release plánu. Piš česky. Vyber klipy dlouhé 10 až 60 sekund. TikTok nastav vždy jako draft. Nevkládej do videa watermark ani text Sleduj na YouTube. Všechny vlastnosti musí být vyplněny."
    },
    {
      "role": "user",
      "content": "Název skladby: [[NÁZEV_SOUBORU_BEZ_MP4]]\nDatum vydání: [[DATUM_VYDÁNÍ]]\nSpotify URL: https://open.spotify.com/artist/3dFUhelmNR3kaxu0S54ZMu\nMetadata videa: [[DÉLKA_VIDEA]] sekund\nPřepis s časovými značkami: [[TRANSKRIPT_SEGMENTS]]"
    }
  ],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "release_plan",
      "strict": true,
      "schema": [[OBSAH_SOUBORU_release_plan.json]]
    }
  }
}
```

V Make nelze do pole `schema` vložit přímo cestu k souboru. Otevři v textovém editoru soubor `schemas/release_plan.json`, zkopíruj celý jeho obsah a vlož ho místo `[[OBSAH_SOUBORU_release_plan.json]]` bez uvozovek.

Do pole s názvem skladby napiš pro první test přímo:

```text
Mosty mezi námi
```

Do pole data vydání napiš:

```text
2026-10-02
```

Do pole přepisu namapuj `segments` z transkripčního modulu.

Klikni na **Save**. Klikni na **Run once**. Otevři odpověď modulu. V odpovědi musí být:

```text
choices → 1 → message → content
```

Hodnota `content` musí být JSON obsahující `release_id`, `clips` a `posts`.

---

## 12. Rozparsování release plánu v Make

1. Klikni na `+` vpravo od Groq chat modulu.
2. Vyhledej `JSON`.
3. Vyber **Parse JSON**.
4. Do pole **JSON string** namapuj:

```text
choices[1].message.content
```

5. Klikni na **Data structure**.
6. Klikni na **Add**.
7. Vyber **Generate**.
8. Do pole vlož obsah souboru `schemas/release_plan.json`.
9. Klikni na **Save**.
10. Klikni na **Save** u modulu.

Make nyní rozpozná jednotlivé klipy jako položky `clips[]`.

---

## 13. Přidání úlohy do Render fronty

1. Klikni na `+` vpravo od JSON modulu.
2. Vyber **HTTP > Make a request**.
3. Do pole **URL** vlož URL Renderu a doplň `/v1/jobs`:

```text
https://stork-command-queue.onrender.com/v1/jobs
```

4. V poli **Method** vyber `POST`.
5. Přidej header:

```text
Name: Authorization
Value: Bearer HESLO_FRONTY
```

6. Nahraď `HESLO_FRONTY` heslem uloženým v Renderu a `.env`.
7. Přidej header:

```text
Name: Content-Type
Value: application/json
```

8. V poli **Body type** vyber `Raw`.
9. V poli **Content type** vyber `application/json`.
10. Vlož tento JSON:

```json
{
  "job_id": "MOSTY_MEZI_NAMI_001",
  "release_id": "MOSTY_MEZI_NAMI_001",
  "source": "Mosty_mezi_nami.mp4",
  "release_plan": [[NAMAPOVANY_RELEASE_PLAN]]
}
```

11. Nahraď `[[NAMAPOVANY_RELEASE_PLAN]]` celým výstupem z modulu **Parse JSON**.
12. Klikni na **Save**.

Při prvním testu musí být soubor `Mosty_mezi_nami.mp4` uložený v lokální složce:

```text
/home/TVE_UZIVATELSKE_JMENO/STORK_COMMAND/input/Mosty_mezi_nami.mp4
```

Zkopíruj ho z Google Drive do této složky také:

```bash
cp "$HOME/Stažené/Mosty_mezi_nami.mp4" "$HOME/STORK_COMMAND/input/Mosty_mezi_nami.mp4"
```

---

## 14. Spuštění notebookového workeru

Nejprve ověř, že `.env` obsahuje správnou Render URL a heslo fronty.

```bash
cd "$HOME/STORK_COMMAND"
source .venv/bin/activate
python server/worker.py
```

Worker vypíše chybové hlášení pouze v případě problému. Terminál nech otevřený. Worker každých 15 sekund kontroluje frontu.

V Make klikni na **Run once**. V Google Drive `INPUT` musí být testovací soubor. Make vytvoří úlohu. Render ji označí jako `queued`. Worker ji vyzvedne a označí jako `processing`.

Po dokončení zkontroluj výstup:

```bash
find "$HOME/STORK_COMMAND/output" -type f
```

Musíš vidět soubory ve složkách:

```text
output/MOSTY_MEZI_NAMI_001/shorts/
output/MOSTY_MEZI_NAMI_001/reels/
output/MOSTY_MEZI_NAMI_001/tiktok/
```

Přehraj video příkazem:

```bash
ffplay "$HOME/STORK_COMMAND/output/MOSTY_MEZI_NAMI_001/shorts/clip_01.mp4"
```

Video musí být svislé. Rozlišení ověř:

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$HOME/STORK_COMMAND/output/MOSTY_MEZI_NAMI_001/shorts/clip_01.mp4"
```

Výsledek musí být:

```text
1080x1920
```

---

## 15. Nastavení automatického spouštění workeru po zapnutí notebooku

Worker musí běžet během zpracování. Nastavíme automatické spouštění přes systemd uživatelskou službu.

Vytvoř službu:

```bash
mkdir -p "$HOME/.config/systemd/user"
nano "$HOME/.config/systemd/user/stork-worker.service"
```

Vlož:

```ini
[Unit]
Description=STORK COMMAND video worker
After=network-online.target

[Service]
Type=simple
WorkingDirectory=%h/STORK_COMMAND
ExecStart=%h/STORK_COMMAND/.venv/bin/python %h/STORK_COMMAND/server/worker.py
Restart=always
RestartSec=15

[Install]
WantedBy=default.target
```

Soubor ulož. Potom spusť:

```bash
systemctl --user daemon-reload
systemctl --user enable stork-worker.service
systemctl --user start stork-worker.service
systemctl --user status stork-worker.service
```

Na posledním řádku musí být `active (running)`.

Když chceš sledovat log:

```bash
journalctl --user -u stork-worker.service -f
```

Log ukončíš klávesami `Ctrl` + `C`.

---

## 16. Nastavení Make scénáře na automatické spuštění

1. V Make otevři scénář.
2. Klikni na ikonu hodin u prvního modulu.
3. Vyber **At regular intervals**.
4. Do pole intervalu napiš `15`.
5. Vyber jednotku `minutes`.
6. Klikni na **Save**.
7. Vpravo nahoře přepni scénář do stavu **ON**.

Make nyní každých 15 minut zkontroluje složku `INPUT`.

Pro první týden nech scénář v tomto režimu. Veřejné publikování na YouTube, Instagram a TikTok nepřidávej, dokud ručně nezkontroluješ minimálně tři hotové release balíčky.

---

## 17. Ruční publikování prvního hotového videa

### YouTube Shorts

1. Otevři [youtube.com](https://www.youtube.com/).
2. Klikni na **Create**.
3. Klikni na **Upload videos**.
4. Vyber soubor z `output/MOSTY_MEZI_NAMI_001/shorts/`.
5. Do názvu vlož titulek z `release_plan.json`.
6. Do popisu vlož `caption` a `hashtags`.
7. V části **Audience** vyber `No, it's not made for kids`.
8. V části **Visibility** vyber `Private`.
9. Klikni na **Save**.
10. Video přehraj v soukromém režimu.
11. Pokud je v pořádku, změň viditelnost na `Public`.

### Instagram Reels

1. Otevři Instagram.
2. Klikni na **Create**.
3. Vyber **Reel**.
4. Vyber soubor z `output/MOSTY_MEZI_NAMI_001/reels/`.
5. Vlož caption z `release_plan.json`.
6. Přidej hashtagy.
7. Klikni na **Share**.

### TikTok

1. Otevři TikTok.
2. Klikni na **Upload**.
3. Vyber soubor z `output/MOSTY_MEZI_NAMI_001/tiktok/`.
4. Vlož caption z `release_plan.json`.
5. Nepřidávej do videa text `Sleduj na YouTube`.
6. Klikni na **Post**.

---

## 18. Nejčastější chyby a přesné opravy

### Chyba `QUEUE_TOKEN`

Otevři `.env` a zkontroluj, že řádek vypadá takto:

```dotenv
QUEUE_TOKEN=stejne-heslo-jako-v-Renderu
```

Na Renderu otevři **Environment** a zkontroluj stejnou hodnotu v `QUEUE_TOKEN`. Po změně klikni na **Save Changes** a počkej na nový deployment.

### Chyba `401 unauthorized`

V Make zkontroluj header:

```text
Authorization: Bearer HESLO_FRONTY
```

Mezi `Bearer` a heslem musí být právě jedna mezera.

### Chyba `No such file or directory`

Zkontroluj, že video existuje:

```bash
ls -lh "$HOME/STORK_COMMAND/input/Mosty_mezi_nami.mp4"
```

Pokud soubor neexistuje, zkopíruj ho znovu do složky `input`.

### Chyba `ffmpeg not found`

Spusť:

```bash
sudo apt update
sudo apt install -y ffmpeg
```

Potom restartuj worker:

```bash
systemctl --user restart stork-worker.service
```

### Groq vrací chybu 400 u schema

Otevři `schemas/release_plan.json`. Zkontroluj, že každý objekt obsahuje:

```json
"additionalProperties": false
```

Zkontroluj také, že všechny názvy z `properties` jsou uvedené v poli `required`. V tomto balíčku je schema již připravené pro Strict Structured Outputs.[1]

### Video má špatný výřez

V první verzi se používá středový výřez obrazu. Pokud je zpěvák mimo střed, video může být oříznuté. V takovém případě nejprve ručně použij jiný klip v release plánu. Automatické sledování obličeje se přidá až do V2.

### Make vytvořil stejnou úlohu dvakrát

Použij jedinečnou hodnotu `job_id`, například:

```text
MOSTY_MEZI_NAMI_001
```

Stejný `job_id` fronta nepřidá podruhé.

---

## 19. Kontrolní seznam před běžným používáním

Před zapnutím pravidelného Make scénáře musí být splněno všech deset bodů:

1. `ffmpeg -version` funguje.
2. `ffprobe -version` funguje.
3. `.env` obsahuje správnou `QUEUE_BASE_URL`.
4. `.env` obsahuje správný `QUEUE_TOKEN`.
5. Render `/health` vrací `{"ok":true}`.
6. Groq API key funguje.
7. Google Drive obsahuje složky `INPUT`, `OUTPUT`, `ARCHIVE`, `DATA`.
8. Worker má stav `active (running)`.
9. Testovací video vytvoří soubor `1080x1920`.
10. Veřejné publikování je stále ruční.

Po splnění všech bodů můžeš do `INPUT` vkládat další MP4 soubory. Pro každý nový release změň v Make `release_id` a zkontroluj název skladby před spuštěním.

---

## Reference

[1]: https://console.groq.com/docs/structured-outputs "Groq Structured Outputs"
[2]: https://console.groq.com/docs/speech-to-text "Groq Speech to Text"
[3]: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post "TikTok Content Posting API Direct Post"
[4]: https://help.make.com/webhooks "Make Webhooks Help Center"
