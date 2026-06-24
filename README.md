# Tellofix XDCC Search API

Eine selbst gehostete XDCC-Suchmaschine als REST-API, verpackt in Docker.

## Schnellstart

### 1. Repository klonen

    git clone https://github.com/fhu123/tellofix-xdcc.git
    cd tellofix-xdcc

### 2. Umgebungsvariablen konfigurieren

    cp .env.example .env
    nano .env

Trage deine eigenen Werte ein:

    IRC_SERVER=irc.abjects.net
    IRC_PORT=6667
    IRC_NICKNAME=dein_nickname_hier
    IRC_CHANNELS=#BEAST-XDCC

    MYSQL_ROOT_PASSWORD=sicheresPasswort
    MYSQL_DATABASE=xdcc_test
    MYSQL_USER=xdcc
    MYSQL_PASSWORD=sicheresPasswort

    APP_PORT=8888

Die MySQL-Datenbank wird beim ersten Start automatisch angelegt.

### 3. Container starten

    docker compose up -d

### 4. API aufrufen

    http://localhost:8888

## Container verwalten

    docker compose logs -f      # Logs anzeigen
    docker compose down         # Stoppen
    docker compose restart      # Neu starten
    docker compose down -v      # Stoppen + DB loeschen

## Sicherheitshinweise

- .env niemals in Git eintragen (bereits in .gitignore)
- Starke Passwoerter verwenden
- API nicht ohne Authentifizierung ins Internet stellen
