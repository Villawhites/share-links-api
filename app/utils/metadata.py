import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

async def extract_metadata(url: str) -> Dict[str, Any]:
    """
    Extrae metadata básica de una URL
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return {"platform": "generic", "url": url}
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Detectar plataforma
                platform = detect_platform(url)
                
                # Extraer metadata
                og_title = soup.find("meta", property="og:title")
                og_description = soup.find("meta", property="og:description")
                og_image = soup.find("meta", property="og:image")
                
                return {
                    "platform": platform,
                    "url": url,
                    "title": og_title["content"] if og_title else None,
                    "description": og_description["content"] if og_description else None,
                    "thumbnail_url": og_image["content"] if og_image else None
                }
    except Exception as e:
        return {"platform": "generic", "url": url, "error": str(e)}

def detect_platform(url: str) -> str:
    """
    Detecta la plataforma del URL
    """
    if "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "pinterest.com" in url:
        return "pinterest"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    else:
        return "generic"