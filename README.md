# Rakuten Daily Ranking Bot

楽天市場の日間ランキングを取得して、Slackに送信するボット。

## 준비

### 1. Slack Bot Token 준비

https://api.slack.com/apps 에서:
- Bot User OAuth Token 복사
- Scopes에 `chat:write` 있는지 확인

### 2. 환경변수 설정

```bash
# macOS / Linux
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_CHANNEL="#채널명 또는 채널ID"

# Windows PowerShell
$env:SLACK_BOT_TOKEN="xoxb-..."
$env:SLACK_CHANNEL="#채널명 또는 채널ID"
```

## 실행

### 설치

```bash
pip install -r requirements.txt
```

### 실행

```bash
python main.py
```

실행 후:
- `[main] fetching Rakuten daily ranking...`
- `[main] fetched N items`
- `[main] done`

메시지가 나오면 성공입니다.

## 파일 구성

- `scraper.py` - BeautifulSoup으로 Rakuten 랭킹 페이지 크롤링
- `slack_notifier.py` - Block Kit 형식으로 Slack에 메시지 전송
- `main.py` - 메인 진입점
- `requirements.txt` - 의존성 패키지

## 스케줄 설정 (Windows)

작업 스케줄러에서:
1. 새 작업 만들기
2. 트리거: 매일 오전 9시
3. 작업: `python C:\Users\user\rakuten-ranking-bot\main.py`

또는 cron (Linux/macOS):
```bash
0 9 * * * cd ~/rakuten-ranking-bot && SLACK_BOT_TOKEN="xoxb-..." SLACK_CHANNEL="#채널" python main.py
```
