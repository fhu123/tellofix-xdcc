# Tellofix XDCC Searcher

Self-hosted XDCC search engine built on Docker.
Built with a little help from AI on a summer afternoon.

## Features
- Local search in cached XDCC pack database
- Live scraper via SunXDCC, xdcc.eu, xdcc.rocks
- German / International language filter toggle
- One-Click download command generator
- Runs fully in Docker

## Quick Start
1. Clone this repo
2. Copy .env.example to .env and fill in your IRC credentials
3. Run: docker compose up -d
4. Open: http://localhost:9999

## Test IRC Servers
- irc.abjects.net port 6667 channel #BEAST-XDCC
- irc.abjects.net port 6667 channels #moviegods AND #mg-chat (join both!)
- irc.scenep2p.net port 6667 channel #THE.SOURCE
- irc.rizon.net port 6697 channel #nibl

## Security
- Never commit your .env file - it contains credentials
- .gitignore already excludes .env and mysql/

## License
MIT
