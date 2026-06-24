# Tellofix XDCC Search API

A self-hosted XDCC search engine as a REST API, packaged in Docker.

## Quick Start

### 1. Clone the Repository

    git clone https://github.com/fhu123/tellofix-xdcc.git
    cd tellofix-xdcc

### 2. Configure Environment Variables

    cp .env.example .env
    nano .env

Default test credentials are already set (tellofix / tellofix).
IMPORTANT: Change passwords in production!

### 3. Start the Containers

    docker compose up -d

### 4. Access the API

    http://localhost:8888

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Status / home |
| GET | /search?q=moviename | Search XDCC packages |

## Managing Containers

    docker compose logs -f        # Show logs
    docker compose down           # Stop
    docker compose restart        # Restart
    docker compose down -v        # Stop + delete database

## Security Notes

- Never commit .env to Git (already in .gitignore)
- Use strong passwords in production
- Do not expose the API to the internet without authentication
