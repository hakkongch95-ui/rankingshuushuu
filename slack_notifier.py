import os
from datetime import datetime, timezone, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

KST = timezone(timedelta(hours=9))


def _build_blocks(items: list[dict]) -> list[dict]:
    today = datetime.now(KST).strftime("%Y년 %m월 %d일")
    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🏆 라쿠텐 일간 랭킹 TOP {len(items)}  |  {today}",
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    medal = {1: "🥇", 2: "🥈", 3: "🥉"}

    for item in items:
        try:
            rank_num = int("".join(filter(str.isdigit, item.get("rank", "0"))) or "0")
        except ValueError:
            rank_num = 0

        icon = medal.get(rank_num, f"*{rank_num}위*")
        name = item.get("name", "(이름 없음)").strip()
        price = item.get("price", "").strip()
        url = item.get("url", "")

        name_text = f"<{url}|{name}>" if url else name
        price_text = f"  `{price}`" if price else ""

        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{icon}  {name_text}{price_text}",
                },
            }
        )

    blocks.append({"type": "divider"})
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📦 출처: <https://ranking.rakuten.co.jp/|라쿠텐 랭킹>  •  자동 수집 봇",
                }
            ],
        }
    )
    return blocks


def send_ranking(items: list[dict]) -> bool:
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL", "#general")

    if not token:
        print("[notifier] SLACK_BOT_TOKEN not set")
        return False

    client = WebClient(token=token)

    if not items:
        fallback_text = "⚠️ 오늘 라쿠텐 랭킹 데이터를 가져오지 못했습니다."
        try:
            client.chat_postMessage(channel=channel, text=fallback_text)
        except SlackApiError as e:
            print(f"[notifier] slack error: {e.response['error']}")
            return False
        return True

    blocks = _build_blocks(items)
    fallback = f"라쿠텐 일간 랭킹 TOP {len(items)}"

    try:
        client.chat_postMessage(
            channel=channel,
            text=fallback,
            blocks=blocks,
            unfurl_links=False,
            unfurl_media=False,
        )
        print(f"[notifier] sent {len(items)} items to {channel}")
        return True
    except SlackApiError as e:
        print(f"[notifier] slack error: {e.response['error']}")
        return False
