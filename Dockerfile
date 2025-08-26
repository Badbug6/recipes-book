# Fase 1: Scegliere un'immagine di base
# Partiamo da un'immagine Python 3.10 ufficiale e "slim", che è leggera ma completa.
FROM python:3.10-slim

# Fase 2: Impostare l'ambiente di lavoro
# Creiamo una cartella /app all'interno del container e la impostiamo come directory principale.
WORKDIR /app

# Fase 3: Installare le dipendenze
# Copiamo *solo* il file dei requisiti. Grazie alla cache di Docker, questo passaggio
# verrà saltato nelle build successive se il file non cambia, rendendo tutto più veloce.
COPY requirements.txt .

# Eseguiamo l'installazione delle librerie elencate nel file.
# --no-cache-dir è una buona pratica per mantenere l'immagine più leggera.
RUN pip install --no-cache-dir -r requirements.txt

# Fase 4: Copiare il codice dell'applicazione
# Ora copiamo tutto il resto del nostro progetto (app.py, indexer.py, le cartelle static/ e templates/)
# nella cartella /app del container.
COPY . .

# Fase 5: Esporre la porta
# Dichiariamo che la nostra applicazione, una volta avviata, ascolterà sulla porta 8080.
# Questa è una documentazione per Docker.
EXPOSE 8080

# Fase 6: Definire il comando di avvio
# Questo è il comando che verrà eseguito automaticamente quando il container parte.
# Lancia il nostro server di produzione Waitress.
CMD [ "python", "app.py" ]