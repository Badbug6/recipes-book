# Recipe Book - Ricettario Personale

Una semplice applicazione web self-hosted e containerizzata (con Docker) per indicizzare, cercare e gestire la tua collezione personale di ricette in formato HTML.

---

## ✨ Funzionalità

-   **Indicizzazione Automatica**: Analizza una cartella (incluse le sottocartelle) di file HTML per costruire un indice di ricerca.
-   **Ricerca Veloce**: Trova istantaneamente le ricette cercando nei titoli o nei tag.
-   **Scoperta delle Categorie**: Considera automaticamente le tue cartelle come categorie.
-   **Ricerca con Autocompletamento**: Un campo di ricerca intelligente ti aiuta a trovare rapidamente le categorie, anche se ne hai centinaia.
-   **Suggerimenti Casuali**: Mostra una selezione casuale di categorie sulla homepage per aiutarti a riscoprire vecchie ricette.
-   **Rilevamento Duplicati**: Trova le ricette con titoli duplicati e le sposta automaticamente in una cartella `duplicati` per aiutarti a mantenere la tua collezione pulita.
-   **Aggiornamento Indice con un Click**: Aggiorna l'intero indice delle ricette direttamente dall'interfaccia web, con una barra di avanzamento visibile nel terminale.
-   **Completamente Containerizzata**: L'intera applicazione viene eseguita in un container Docker, rendendo l'installazione e la gestione incredibilmente semplici.

## 🛠️ Tecnologie Utilizzate

-   **Backend**: Python 3.10, Flask, Waitress (Server WSGI)
-   **Parsing HTML**: BeautifulSoup4
-   **Frontend**: HTML, CSS, JavaScript (Vanilla)
-   **Container**: Docker & Docker Compose

## 🚀 Per Iniziare

Questi sono i passaggi per far girare Recipe Book sul tuo computer o server.

### Prerequisiti

1.  **Docker** e **Docker Compose**: Assicurati che siano installati sulla tua macchina. Il modo più semplice è installare [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2.  **Una cartella di ricette**: Devi avere i tuoi file di ricette in formato `.html` pronti.

### Installazione e Configurazione

1.  **Clona o Scarica il Progetto**
    Scarica tutti i file di questo progetto e mettili in una cartella (es. `progetto_ricette`).

2.  **Aggiungi le Tue Ricette**
    Copia tutti i tuoi file `.html` (e le loro sottocartelle) dentro la directory `le-mie-ricette`. La struttura può essere profonda a piacere:
    ```
    /le-mie-ricette
        ├── Primi Piatti/
        │   ├── pasta.html
        │   └── risotto.html
        └── Dolci/
            └── torte/
                └── torta_di_mele.html
    ```

3.  **Avvia l'Applicazione**
    Apri un terminale nella cartella principale del progetto ed esegui un singolo comando:
    ```bash
    docker-compose up -d --build
    ```
    -   `--build`: La prima volta, questo comando costruirà l'immagine Docker.
    -   `-d`: Avvierà il container in background (modalità "detached").

4.  **Accedi al Tuo Ricettario!**
    Apri il tuo browser web e visita: **http://localhost:8080**

## 📖 Come Usare

1.  **Primo Avvio: Indicizzazione**
    La prima volta che avvii l'app, l'indice sarà vuoto. Clicca il bottone **"Aggiorna Indice Ricette"**. Vedrai un messaggio di caricamento. Il progresso dell'operazione sarà visibile nel terminale dove hai eseguito il comando Docker.

2.  **Trovare una Ricetta**
    Hai due modi per cercare:
    -   **Trova una Categoria**: Inizia a scrivere nel campo di ricerca superiore. Apparirà una lista di categorie (le tue cartelle) che corrispondono. Puoi anche cliccare sui suggerimenti casuali che appaiono sotto.
    -   **Cerca in tutte le ricette**: Usa la seconda barra di ricerca per trovare ricette in base a parole nel loro titolo o nei loro tag.

3.  **Gestione dei Duplicati**
    Durante il processo di indicizzazione, se lo script trova due file con lo stesso titolo, il primo verrà indicizzato e il secondo verrà **automaticamente spostato** nella cartella `duplicati`, mantenendo la sua struttura di cartelle originale.

## ⚙️ Gestione del Container

-   **Per vedere i log in tempo reale** (utile durante l'indicizzazione):
    ```bash
    docker-compose logs -f
    ```
-   **Per fermare l'applicazione**:
    ```bash
    docker-compose down
    ```
-   **Per riavviare l'applicazione** (dopo averla fermata):
    ```bash
    docker-compose up -d
    ```

## 📂 Struttura del Progetto
```
├── le-mie-ricette/ # Dove metti i tuoi file di ricette .html
├── static/
│ └── style.css # Stili CSS personalizzati per l'interfaccia
├── templates/
│ └── index.html # Il template HTML dell'applicazione
├── app.py # Il server web Flask
├── indexer.py # Lo script che analizza e indicizza i file
├── recipes.json # Il file "database" generato dall'indicizzatore
├── requirements.txt # Le dipendenze Python del progetto
├── Dockerfile # Le istruzioni per costruire l'immagine Docker
└── docker-compose.yml # Il file per avviare e gestire l'applicazione facilmente
```