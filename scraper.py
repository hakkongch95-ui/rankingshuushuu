import asyncio
from playwright.async_api import async_playwright

RAKUTEN_RANKING_URL = "https://ranking.rakuten.co.jp/"


async def fetch_ranking() -> list[dict]:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
                viewport={"width": 1280, "height": 800},
            )

            # Stealth: hide webdriver flag
            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            page = await context.new_page()
            await page.goto(RAKUTEN_RANKING_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            items = await page.evaluate("""
                () => {
                    const results = [];
                    const cards = document.querySelectorAll(
                        '.rankingItem, [class*="ranking-item"], [class*="rnkgItem"]'
                    );
                    cards.forEach((card, idx) => {
                        if (idx >= 10) return;
                        const rank = card.querySelector(
                            '[class*="rank"], [class*="number"], .num'
                        );
                        const name = card.querySelector(
                            '[class*="name"], [class*="title"], .itemName, a[class*="item"]'
                        );
                        const price = card.querySelector(
                            '[class*="price"], .price'
                        );
                        const link = card.querySelector('a');
                        const img = card.querySelector('img');
                        results.push({
                            rank: rank ? rank.textContent.trim() : String(idx + 1),
                            name: name ? name.textContent.trim() : '',
                            price: price ? price.textContent.trim() : '',
                            url: link ? link.href : '',
                            image: img ? img.src : '',
                        });
                    });
                    return results;
                }
            """)

            # Fallback selector if primary yields nothing
            if not items:
                items = await page.evaluate("""
                    () => {
                        const results = [];
                        const links = document.querySelectorAll(
                            'a[data-ratid*="rank"], a[href*="item.rakuten"]'
                        );
                        links.forEach((a, idx) => {
                            if (idx >= 10) return;
                            results.push({
                                rank: String(idx + 1),
                                name: a.textContent.trim().slice(0, 60),
                                price: '',
                                url: a.href,
                                image: '',
                            });
                        });
                        return results;
                    }
                """)

            if not items:
                html_snippet = await page.content()
                print(f"[scraper] page title: {await page.title()}")
                print(f"[scraper] HTML snippet (first 3000 chars):\n{html_snippet[:3000]}")

            await browser.close()
            return [item for item in items if item.get("name")]

    except Exception as e:
        print(f"[scraper] error: {e}")
        return []


def get_ranking() -> list[dict]:
    return asyncio.run(fetch_ranking())
