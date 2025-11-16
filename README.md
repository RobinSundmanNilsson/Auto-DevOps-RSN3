# 📘 SMHI Weather Dashboard - DevOps Pipeline

Detta dokument beskriver projektets arkitektur, funktionalitet,
CI/CD-pipeline, tester och designval.

------------------------------------------------------------------------

## 🌦️ Funktionalitet

-   Hämtar väderprognoser från SMHI:s öppna API.
-   Extraherar temperatur, tid, nederbörd m.m.
-   Bearbetar datan till ett Pandas-DataFrame.
-   Körs som Docker-container i Azure Web App via Docker Hub.

------------------------------------------------------------------------

## 🧪 Tester

Projektet innehåller två typer av tester: ett mockat enhetstest och ett integrationstest mot SMHI:s riktiga API. 
Båda körs automatiskt i pipelinen när du pushar till main, och båda kan stoppa byggsteget om de misslyckas.

### ✔ Enhetstester (mockade)

Fil: `test_process_smhi_data.py`
Detta test mockar SMHI-anropet med unittest.mock.patch och testar endast applikationens interna logik:

- Databehandling
- Struktur på det skapade DataFrame
- Avrundning av temperatur
- Logik för rain/snow

Detta är helt frikopplat från nätverk och API, vilket gör det stabilt och reproducerbart.

### ✔ Integrationstest

Fil: `test_api.py`
Detta test anropar SMHI:s verkliga API och verifierar att applikationen kan:

- Hämtar data från API:t
- Läser JSON-strukturen
- Hantera timeSeries korrekt

Eftersom det anropar SMHI:s riktiga API är testet känsligare för yttre faktorer, 
men det körs fortfarande tillsammans med övriga tester i pipelinen.

### ✔ Hur testerna körs i pipelinen

Pipelinen kör:

`pytest -q`

Detta innebär att alla tester i projektet körs automatiskt både vid:

- push till main
- manuellt med `workflow_dispatch`

Om något test misslyckas:

- testloggar sparas (om workflow_dispatch + log_errors = true)
- tests-jobbet failar
- build-and-push-jobbet körs inte

Detta säkerställer att endast godkänd kod byggs och publiceras.

------------------------------------------------------------------------

## 🔧 CI/CD Pipeline (GitHub Actions)

Pipeline-filen ligger i `.github/workflows/main-rsn3.yml`.

### Innehåller två jobb:

------------------------------------------------------------------------

### **1. tests**

-   Körs på push och workflow_dispatch.
-   Installerar beroenden.
-   Kör pytest och genererar loggfil.
-   Laddar upp loggar som artefakt *om och endast om*:
    -   workflow_dispatch används,
    -   parametern `log_errors=true`,
    -   testerna misslyckas.

------------------------------------------------------------------------

### **2. build-and-push**

-   Körs endast om testerna är godkända (`needs: tests` +
    `if: result == success`).
-   Bygger Docker-image med Docker Buildx.
-   Taggar imagen med:
    -   latest
    -   commit-SHA
    -   branch-namn
-   Pushar imagen till Docker Hub.

Azure Web App är konfigurerad att automatiskt hämta senaste imagen från
Docker Hub.

------------------------------------------------------------------------

## 🔐 GitHub Environment & Secrets

För att pipelinen ska fungera krävs environment:

    DOCKER_HUB

I denna environment ska följande secrets finnas:

  Secret                    Funktion
  ------------------------- -------------------------
  **DOCKER_HUB_USERNAME**   Docker Hub användarnamn
  **DOCKER_HUB_TOKEN**      Docker Hub Access Token

Access Token genereras via Docker Hub

------------------------------------------------------------------------

## 🐳 Docker

### Bygg lokalt:

``` bash
docker build -t smhi_weather_dashboard .
```

### Kör lokalt:

``` bash
docker run -p 8501:8501 smhi_weather_dashboard
```

------------------------------------------------------------------------

## 🧩 Designval

### 1️⃣ Mockade tester i CI

För att pipelines ska vara stabila och reproducerbara mockas externa
API-anrop.\
Detta säkerställer att fel eller långsamhet hos SMHI inte stoppar
utvecklingsflödet.

### 2️⃣ needs + if för logik och beroenden

`build-and-push` körs endast om `tests`-jobbet är grönt.\
Detta garanterar kvalitet före distribution.

### 3️⃣ workflow_dispatch-parameter för loggar

Ger kontroll och gör pipelinen mer flexibel:\
Man kan begära detaljerade felsökningsloggar endast när det behövs.

### 4️⃣ Docker tag-strategi

Tre tags används: - `latest` för Azure Web App. - commit-SHA för
spårbarhet. - branch-namn för parallella miljöer.

### 5️⃣ Docker Hub som registry

Azure Web App drar automatiskt senaste imagen från Docker Hub.\
Detta ger en enkel och robust deploy-modell.

------------------------------------------------------------------------

## Dashboard Preview

![alt text](assets/SMHI_Weather_Forecast.png)
