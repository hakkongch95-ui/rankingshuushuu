import httpx
import time
from bs4 import BeautifulSoup

RAKUTEN_RANKING_URL = "https://ranking.rakuten.co.jp/"


def fetch_ranking() -> list[dict]:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="131", "Chromium";v="131"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
        }

        # Add delay to avoid rate limiting
        time.sleep(3)

        response = httpx.get(
            RAKUTEN_RANKING_URL,
            headers=headers,
            timeout=30,
            follow_redirects=True,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        items = []
        # Rakuten ranking page structure: look for ranking items
        ranking_items = soup.find_all(
            class_=lambda x: x and any(
                keyword in x.lower() for keyword in ["ranking", "item", "product"]
            )
        )

        for idx, item in enumerate(ranking_items[:15]):
            if idx >= 10:
                break

            # Extract rank
            rank_elem = item.find(class_=lambda x: x and "rank" in x.lower())
            rank = rank_elem.get_text(strip=True) if rank_elem else str(idx + 1)

            # Extract product name and link
            link_elem = item.find("a", href=True)
            if not link_elem:
                continue

            name = link_elem.get_text(strip=True)
            url = link_elem.get("href", "")
            if url and not url.startswith("http"):
                url = "https://ranking.rakuten.co.jp" + url

            # Extract price
            price_elem = item.find(class_=lambda x: x and "price" in x.lower())
            price = price_elem.get_text(strip=True) if price_elem else ""

            # Extract image
            img_elem = item.find("img")
            image = img_elem.get("src", "") if img_elem else ""

            items.append(
                {
                    "rank": rank,
                    "name": name[:60] if name else "(無し)",
                    "price": price,
                    "url": url,
                    "image": image,
                }
            )

        if items:
            print(f"[scraper] fetched {len(items)} items from HTML")
        else:
            print(f"[scraper] no items found in HTML")
            print(f"[scraper] page status: {response.status_code}")

        return items

    except httpx.HTTPStatusError as e:
        print(f"[scraper] http status error: {e.response.status_code}")
        return []
    except Exception as e:
        print(f"[scraper] error: {e}")
        return []


def get_ranking() -> list[dict]:
    return fetch_ranking()
