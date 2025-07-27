import asyncio
import httpx

async def test_request():
    url = "https://api.marketfiyati.org.tr/api/v2/search"
    payload = {
        "keywords": "biskrem",
        "latitude": 41.0122440263938,
        "longitude": 28.9594652279346,
        "distance": 8,
        "pages": 0,
        "size": 24
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
        print("Sent Headers:")
        print(response.request.headers)   
        print("\nStatus Code:", response.status_code)
        print("\nResponse Body:", response.text[:500])  

asyncio.run(test_request())
