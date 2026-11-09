import re
import asyncio
import datetime
from typing import NamedTuple

import aiohttp
from bs4 import BeautifulSoup

from pyutils import Clogger

DAILY_URL = "https://lospec.com/dailies/"
PALLET_LIST_URL = "https://lospec.com/palette-list/"
# PALLET_API_URL = "https://lospec.com/palettes/api"

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30)

# the page title ends with the date, e.g. "November 9th 2026"
TITLE_DATE_PATTERN = re.compile(r"([A-Z][a-z]+) (\d{1,2})(?:st|nd|rd|th)? (\d{4})")

class DailyDataError(Exception):
    pass

class DailyData(NamedTuple):
    tag: str
    palleteURL: str
    pageDate: datetime.date | None # the date lospec says this daily is for, if it could be read

def parseTag(soup: BeautifulSoup) -> str | None:
    # try a few selectors, newest layout first, so a single markup change doesn't take us down
    candidates = [
        soup.select_one("h1.daily-tag"),
        soup.select_one('h1.daily-name a[href^="/gallery/tags:"]'),
    ]
    for el in candidates:
        if el and el.get_text(strip=True).startswith("#"):
            return el.get_text(strip=True)
    return None

def parsePalletSlug(soup: BeautifulSoup) -> str | None:
    candidates = [
        soup.select_one('div.daily.palette a[href^="/palette-list/"]'),
        soup.select_one('h1.daily-name a[href^="/palette-list/"]'),
    ]
    for el in candidates:
        if el:
            slug = el["href"].rstrip("/").split("/")[-1]
            if slug:
                return slug
    return None

def parsePageDate(soup: BeautifulSoup) -> datetime.date | None:
    title = soup.select_one("h1.daily-page-title")
    match = TITLE_DATE_PATTERN.search(title.get_text()) if title else None
    if not match:
        return None
    try:
        return datetime.datetime.strptime(" ".join(match.groups()), "%B %d %Y").date()
    except ValueError:
        return None

async def getDailyData() -> DailyData:
    """Scrapes the current daily from lospec. Raises DailyDataError on any failure."""
    Clogger.info("Fetching daily data from Lospec...")
    try:
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            async with session.get(DAILY_URL) as response:
                response.raise_for_status()
                html = await response.text()
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        msg = f"Request to {DAILY_URL} failed: {type(e).__name__}: {e}"
        Clogger.error(msg)
        raise DailyDataError(msg) from e

    soup = BeautifulSoup(html, "html.parser")

    tag = parseTag(soup)
    if not tag:
        msg = "Could not find daily tag on the page. The Lospec page layout may have changed."
        Clogger.error(msg)
        raise DailyDataError(msg)

    palletSlug = parsePalletSlug(soup)
    if not palletSlug:
        msg = "Could not find palette slug on the page. The Lospec page layout may have changed."
        Clogger.error(msg)
        raise DailyDataError(msg)

    pageDate = parsePageDate(soup)
    if pageDate is None:
        Clogger.warn("Could not read the date from the Lospec page title, can't verify the daily is current")

    Clogger.info(f"Successfully fetched daily data: Tag - {tag}, Palette Slug - {palletSlug}, Date - {pageDate}")
    return DailyData(tag, PALLET_LIST_URL + palletSlug, pageDate)

# TESTING!!!
if __name__ == "__main__":
    info = asyncio.run(getDailyData())
    print(info)
