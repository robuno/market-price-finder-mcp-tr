This project is a Model Context Protocol (MCP) tool that helps users find the cheapest price for a product in nearby markets based on a natural language prompt that includes both product name and location.

Features
- Parses natural prompts like:
"How much is Eti Tutku in Başakşehir?"
"Çokoprens fiyatı in Başak Mah, Başakşehir"

- Converts textual location into geographic coordinates using OpenStreetMap.
- Queries the MarketFiyati.org.tr API to find real-time product prices in various markets (Migros, A101, Bim, etc.).
- Dynamically updates search location based on user prompt.

Tools
fast-mcp: For building the MCP tool interface
httpx: For asynchronous HTTP requests
OpenStreetMap Nominatim: For geocoding location strings
MarketFiyati API: For product price search