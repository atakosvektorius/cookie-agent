# Agentas interneto slapukams rinkti į BDAR atitikties serverį

Tai BDAR (Bendrojo duomenų apsaugos reglamento) slapukų atitikties įrankis, skirtas padėti svetainėms atitikti Europos Sąjungos duomenų apsaugos reikalavimus. Agentas automatiškai aplanko nurodytas svetaines naudodamas tikrą Firefox naršyklę, surenka įdiegtus slapukus ir rezultatus perduoda atgal į centrinį BDAR atitikties serverį.

</br>

## Kaip veikia

1. Agentas kreipiasi į centrinį serverį (`GET_WORK_URL`) ir gauna domenų paketą apdorojimui.
2. Kiekvienam domenui:
   - Patikrina DNS A įrašą.
   - Patikrina ar atidaryti 443/80 TCP prievadai.
   - Bando atidaryti svetainę per `https://`, jei nepavyksta — per `http://`.
   - Surenka visų įdiegtų slapukų pavadinimus per `driver.get_cookies()`.
3. Rezultatus siunčia atgal į serverį (`PUSH_RESULTS_URL`) su `action: "update"`.
4. Domenai be DNS įrašo arba neatsakantys į HTTP(S) — pažymimi trynimui (`action: "delete"`).
5. Po kiekvieno sėkmingo rezultato agentas atnaujina `HEALTHCHECK_FILE`. Jei failas nepaliečiamas ilgiau nei 120s — Docker healthcheck pažymi konteinerį kaip nesveiką ir jis paleidžiamas iš naujo.

## Technologijos

- **Firefox + geckodriver** — tikra naršyklė headless režimu (per `selenium/standalone-firefox` bazinį image).
- **noVNC + Xvfb** — grafinė sesija pasiekiama per naršyklę (naudinga derinimui).
- **Python + Selenium** — web automatizacija, slapukų rinkimas.
- **dnspython** — DNS A įrašų tikrinimas prieš bandant kontaktuoti domeną.
- **Docker + Docker Swarm** — konteinerizacija ir horizontalus mastelinimas per replikas.

## Architektūra

Docker Compose / Swarm paleidžia du servisus iš to paties `cookie-agent:latest` image:

| Servisas | Užduotis | GET_WORK_URL |
| --- | --- | --- |
| `cookie-agent` | Pagrindinė darbų eilė — nauji domenai | `/api/admin/cookies/getwork` |
| `cookie-agent-deleted` | Anksčiau ištrintų domenų pakartotinis patikrinimas | `/api/admin/deletedcookies/getwork` |

Abu servisai rezultatus siunčia į tą patį `PUSH_RESULTS_URL` endpoint'ą. Replikų kiekis konfigūruojamas per `deploy.replicas` — pagal nutylėjimą 5 pagrindinio agento ir 1 "deleted" agento.

Procesų eiga viename konteineryje (`agent/scrapper_entrypoint.sh`):
1. Paleidžia Selenium stack'ą fone (Xvfb + geckodriver + Selenium serverį prievade `:4444`, noVNC).
2. Laukia kol `http://localhost:4444/status` atsakys.
3. Paleidžia `scrapper.py` amžinoje kilpoje — kiekvienam paketui sukuriama nauja Firefox sesija, apdorojimo pabaigoje ji uždaroma.

## Palaikomos architektūros
- **x86_64 / amd64**
- **arm64 / aarch64** (Apple Silicon, Raspberry Pi 4+ ir kt.)

</br>

## Naudojimas

### 1. Nuklonuokite repozitoriją

```bash
git clone https://github.com/atakosvektorius/agent
cd agent
```

### 2. Sukonfigūruokite Docker Compose

```bash
cp docker-compose.yml.sample docker-compose.yml
```

Atidarykite `docker-compose.yml` ir pakeiskite:

- `API_KEY` — jūsų serverio API raktas.
- `GET_WORK_URL` ir `PUSH_RESULTS_URL` — pakeiskite `172.17.0.1` į jūsų serverio adresą (pvz., `https://jusu-serveris.lt`).
- `LIMIT` — kiek domenų per vieną užklausą traukti (pagal nutylėjimą `10`).
- `deploy.replicas` — kiek lygiagrečių agentų paleisti.

### 3a. Paleidimas per Docker Swarm (rekomenduojama produkcijai)

```bash
docker swarm init
./deployStock.sh
```

`deployStock.sh` surenka image'ą ir paleidžia stack'ą pavadinimu `yourstack`. Stebėti būseną:

```bash
docker stack services yourstack
docker service logs -f yourstack_cookie-agent
```

### 3b. Paleidimas per Docker Compose (vietiniam testavimui)

```bash
./runUpdateThisStack.sh
```

Tai atitinka `docker compose down && docker compose up --build -d`. Pastaba: `deploy.replicas` veikia tik Swarm režime — `docker compose` paleis po vieną kopiją kiekvieno serviso.

</br>

## Aplinkos kintamieji

Visi skaitomi tiesiogiai per `os.getenv` be numatytų reikšmių:

| Kintamasis | Paskirtis |
| --- | --- |
| `API_KEY` | Autentifikacija su backend'u |
| `GET_WORK_URL` | Iš kur traukti domenų paketus |
| `PUSH_RESULTS_URL` | Kur siųsti surinktus slapukus / trynimo užklausas |
| `LIMIT` | Domenų kiekis viename pakete |
| `GECKODRIVER_PATH` | Kelias iki geckodriver binary (`/usr/bin/geckodriver`) |
| `HEALTHCHECK_FILE` | Failas, kurį agentas paliečia po kiekvieno sėkmingo darbo |
| `DB_PATH` | SQLite DB kelias agento būsenai (`/data/cookie_agent.db`) |

## Problemų sprendimai

Logai per terminalą:

```bash
# Compose režimas
docker logs -f cookie-agent
docker logs -f cookie-agent-deleted

# Swarm režimas
docker service logs -f yourstack_cookie-agent
docker service logs -f yourstack_cookie-agent-deleted
```

Rankinis healthcheck būsenos patikrinimas:

```bash
docker inspect --format '{{json .State.Health}}' cookie-agent | jq
```

## Licencija ir kontaktai

Šis projektas sukurtas "Atakos vektorius", https://atakosvektorius.lt
