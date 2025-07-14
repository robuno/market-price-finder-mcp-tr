import re
from typing import Union


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