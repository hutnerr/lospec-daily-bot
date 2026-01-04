import aiohttp
import asyncio
from bs4 import BeautifulSoup

from clogger import Clogger

DAILY_URL = "https://lospec.com/dailies/"
PALLET_LIST_URL = "https://lospec.com/palette-list/"
# PALLET_API_URL = "https://lospec.com/palettes/api"

async def getDailyData() -> tuple[str, str] | None:
    Clogger.info("Fetching daily data from Lospec...")
    async with aiohttp.ClientSession() as session:
        async with session.get(DAILY_URL) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            tag = soup.find("div", class_="daily tag")
            if not tag:
                Clogger.error("Could not find daily tag on the page.")
                return
            
            palletDiv = soup.find("div", class_="daily palette")
            palletSlug = palletDiv.find("a")["href"].split("/")[-1] if palletDiv else None
            if not palletSlug:
                Clogger.error("Could not find palette slug.")
                return
            
            Clogger.info(f"Successfully fetched daily data: Tag - {tag.text.strip()}, Palette Slug - {palletSlug}")
            return (tag.text.strip(), PALLET_LIST_URL + palletSlug)

# TESTING!!!
if __name__ == "__main__":
    info = asyncio.run(getDailyData())
    print(info)