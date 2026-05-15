import sys
from scraper import get_ranking
from slack_notifier import send_ranking


def main() -> int:
    print("[main] fetching Rakuten daily ranking...")
    items = get_ranking()
    print(f"[main] fetched {len(items)} items")

    ok = send_ranking(items)
    if not ok:
        print("[main] failed to send Slack message")
        return 1

    print("[main] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
