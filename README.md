# Jira Assistant Bot — Telegram Bot for Jira Issue Management

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.25-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

A Telegram bot that connects to your Jira workspace, letting you view, create, and edit issues, manage comments, and receive real-time webhook notifications — all from Telegram.

---

## Key Features

- **View Issues** — look up any Jira issue by number, see summary, description, labels, and link
- **Create Issues** — create new Jira stories with title and description directly from Telegram
- **Edit Issues** — update issue title or description
- **Comments** — view and add comments on any issue
- **Ping Users** — send a Telegram notification to a team member about a specific task
- **Webhook Notifications** — real-time Jira event notifications (task created/updated/deleted, comments, attachments, sprints, versions) with per-user event filtering
- **Feedback** — send feedback to the bot admin

---

## Architecture

```
JiraAssistantBot/
├── bot/                        # aiogram 3.x Telegram bot
│   ├── main.py                 # Entry point: Dispatcher + polling
│   ├── states.py               # FSM state groups
│   ├── keyboards.py            # Reply keyboard definitions
│   ├── middlewares.py           # Profile middleware (user loading)
│   └── handlers/
│       ├── start.py            # /start, menu routing
│       ├── auth.py             # Jira credential flow
│       ├── tasks.py            # View, create, edit tasks
│       ├── comments.py         # View and add comments
│       ├── ping.py             # Ping team members
│       ├── settings.py         # Notification toggles
│       └── feedback.py         # Feedback to admin
├── core/                       # Django app
│   ├── models.py               # Profile (Jira credentials, notification prefs)
│   ├── services.py             # ProfileService
│   ├── views.py                # WebhookView (Jira event handler)
│   ├── urls.py                 # /core/jira_webhook endpoint
│   └── tests.py                # Service tests
├── django_microservice/        # Django project config
├── conf/
│   ├── docker/                 # Dockerfiles
│   └── docker-compose.yml
├── Makefile
└── README.md
```

**Services layer**: Business logic in `core/services.py`. Bot handlers call services via `sync_to_async`. Jira API calls also wrapped with `sync_to_async`.

---

## Getting Started

### Prerequisites
- Python 3.12+, PostgreSQL
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Jira Cloud workspace with API access

### Local Development

```bash
cp .env.example .env          # Set TELEGRAM_API_KEY, SECRET_KEY, DB settings
python manage.py migrate
python bot/main.py             # Start the bot
```

### Docker

```bash
cp .env.example .env
make build && make up
```

For Jira webhook notifications, configure a webhook in Jira pointing to your server's `/core/jira_webhook` endpoint.

---

## License

Personal project. All rights reserved.
