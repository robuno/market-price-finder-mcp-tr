from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
# from parser_utils import parse_prompt  # externalized prompt parser
import re
from typing import Union




# Initialize FastMCP server
mcp = FastMCP("market-finder")

# Global coordinates (will be updated from prompt)
# LATITUDE: float = 41.0906203414694
# LONGITUDE: float = 28.811139751321

async def search_market_product(
    keywords: str,
    latitude: float,
    longitude: float,
    distance: int = 4,
    page: int = 0,
    size: int = 24
) -> Optional[Dict[str, Any]]:
    """
    Search for a product by keyword using the Market Fiyatı API.
    Returns the most relevant product's title, lowest price, and market name.
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

            product = data["content"][0]
            title = product.get("title")

            depots = product.get("productDepotInfoList", [])
            if not depots:
                return {"title": title, "price": None, "market": None}

            best_depot = min(depots, key=lambda d: d.get("price", float("inf")))
            return {
                "title": title,
                "price": best_depot.get("price"),
                "market": best_depot.get("marketAdi")
            }

        except Exception:
            return None

@mcp.tool()
async def get_market_product(keywords: str) -> Dict[str, Any] | str:
    """
    MCP tool to search for a product by keywords and return its name, price, and market
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



def parse_prompt(prompt: str) -> Union[dict[str, str], str]:
    """
    Parse a natural language prompt to extract location and product.
    
    Supported patterns:
    - "X konumu için Y"
    - "X'de Y ne kadar"
    - "X'da Y ne kadar"
    - "X civarında Y fiyatı"
    """
    prompt = prompt.lower().strip()

    patterns = [
        r"(?P<location>.+?)\s+konumu için\s+(?P<product>.+?)\s+.*",
        r"(?P<location>.+?)'da\s+(?P<product>.+?)\s+ne kadar",
        r"(?P<location>.+?)'de\s+(?P<product>.+?)\s+ne kadar",
        r"(?P<location>.+?) civarında\s+(?P<product>.+?) fiyat[ıi]?",
    ]

    for pattern in patterns:
        match = re.match(pattern, prompt)
        if match:
            return {
                "location": match.group("location").strip(),
                "product": match.group("product").strip()
            }

    return "Could not extract location and product. Please provide a clearer input."



if __name__ == "__main__":
    mcp.run(transport='stdio')

