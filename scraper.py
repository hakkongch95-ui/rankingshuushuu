import os
import httpx

RAKUTEN_API_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628"


def fetch_ranking() -> list[dict]:
    app_id = os.environ.get("RAKUTEN_APP_ID")
    if not app_id:
        print("[scraper] RAKUTEN_APP_ID not set")
        return []

    try:
        params = {
            "applicationId": app_id,
            "format": "json",
            "genreId": 0,
            "page": 1,
        }

        response = httpx.get(RAKUTEN_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = []
        for idx, item in enumerate(data.get("Items", [])):
            if idx >= 10:
                break

            items.append(
                {
                    "rank": str(idx + 1),
                    "name": item.get("Item", {}).get("itemName", ""),
                    "price": f"¥{item.get('Item', {}).get('itemPrice', '')}",
                    "url": item.get("Item", {}).get("itemUrl", ""),
                    "image": item.get("Item", {}).get("smallImageUrl", ""),
                }
            )

        return items

    except httpx.HTTPStatusError as e:
        print(f"[scraper] http status error: {e.response.status_code}")
        print(f"[scraper] response: {e.response.text[:500]}")
        return []
    except httpx.HTTPError as e:
        print(f"[scraper] http error: {e}")
        return []
    except Exception as e:
        print(f"[scraper] error: {e}")
        return []


def get_ranking() -> list[dict]:
    return fetch_ranking()
