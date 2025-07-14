from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
from parser_utils import parse_prompt  # externalized prompt parser
import re
from typing import Union




# Initialize FastMCP server
mcp = FastMCP("market-finder")

# Global coordinates (will be updated from prompt)
# LATITUDE: float = 41.0906203414694
# LONGITUDE: float = 28.811139751321

LATITUDE: float | None = None
LONGITUDE: float | None = None

async def search_market_product(
    keywords: str,
    latitude: float,
    longitude: float,
    distance: int = 4,
    page: int = 0,
    size: int = 24
) -> Optional[list[dict[str, Any]]]:
    """
    Search for products by keyword using the Market Fiyatı API.
    Returns a list of products, each with title, lowest price, and market name.
    """
    url = "https://api.marketfiyati.org.tr/api/v2/search"
    payload = {
        "keywords": keywords,
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance,
        "pages": page,
        "size": size
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            if not data.get("content"):
                return None

            results = []
            for product in data["content"]:
                title = product.get("title")
                depots = product.get("productDepotInfoList", [])
                if not depots:
                    results.append({"title": title, "price": None, "market": None})
                    continue
                best_depot = min(depots, key=lambda d: d.get("price", float("inf")))
                results.append({
                    "title": title,
                    "price": best_depot.get("price"),
                    "market": best_depot.get("marketAdi")
                })
            return results

        except Exception:
            return None

@mcp.tool()
async def get_market_product(keywords: str) -> list[dict[str, Any]] | str:
    """
    MCP tool to search for products by keywords and return a list of their name, price, and market
    using the current LATITUDE and LONGITUDE values.
    """
    global LATITUDE, LONGITUDE
    result = await search_market_product(keywords, latitude=LATITUDE, longitude=LONGITUDE)
    if not result:
        return "Product not found."
    return result

@mcp.tool()
async def get_coordinates_from_address(location: str) -> Dict[str, float] | str:
    """
    Convert a written location into latitude and longitude using OpenStreetMap.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "market-finder/1.0"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data:
                return "Location not found."

            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"])
            }
        except Exception:
            return "Error occurred while retrieving coordinates."

@mcp.tool()
async def find_cheapest_product_by_location(prompt: str) -> dict[str, Any] | str:
    """
    Extracts location and product from the given natural language prompt, converts
    the location to coordinates, updates the global LATITUDE and LONGITUDE values,
    and finds the cheapest market offering that product.
    """
    global LATITUDE, LONGITUDE

    parsed = parse_prompt(prompt)
    if isinstance(parsed, str):
        return parsed

    location_text = parsed["location"]
    product_text = parsed["product"]

    coords = await get_coordinates_from_address(location_text)
    if isinstance(coords, str):
        return f"Location error: {coords}"

    LATITUDE = coords["latitude"]
    LONGITUDE = coords["longitude"]

    result = await get_market_product(product_text)
    return result


if __name__ == "__main__":
    mcp.run(transport='stdio')

