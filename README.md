# Phone-Free Night

Trivia-host SaaS, refined from Borussia Dortmund Fan Mode and Ideabrowser
verified research. First customer: an independent bar trivia host who runs
weekly, already pays $19-$29/month for trivia software, and complains about
cheating. Phone-free-minute scoring is a feature, not a standalone category.

Repo: https://github.com/ToXMon/phone-free-night (private by default;
make it public with `gh repo edit ToXMon/phone-free-night --visibility public`
if you want it public).

## Landing page: the free Starter Kit

Open `/starter-kit/` for the host landing page: hero, how a night runs,
what is in the kit, pricing, and honest FAQ. Submitting the form saves a
Lead and shows the download page, with printable table tents at
`/starter-kit/table-tent/` and a 60-second host script at
`/starter-kit/host-script/`. Research summaries live in `docs/research/`.

## What this scaffold does

- Hosts log in, create an event in minutes, and get a 6-character join code.
- Guests join without an account, by code or QR link, and get a guest token URL.
- Guests earn phone-free minutes while locked, lose the streak on unlock,
  and see a live leaderboard that refreshes with HTMX every 5 seconds.
- Hosts can go live, pause for intermission, end an event, and draw a
  raffle weighted by entries (1 entry for joining, plus 1 per 10 minutes).
- The raffle is commit-reveal in miniature: a seed and its SHA-256 hash are
  stored, so the draw can be checked after the fact.
- Django admin lets a host manage their own events.
- A read-only DRF API serves the same leaderboard at
  `/api/events/<id>/leaderboard/`.

## What this scaffold deliberately does not do

- No Stripe billing yet. Pricing from research is free for 1 event/month
  and $19/month for weekly hosts, plus a 15% sponsor prize-pool take to
  validate with the first 10 venues.
- No embedded wallets, no tradable token, no on-chain VRF, no sponsor
  escrow. Points live in the database. Those are later stages.
- No perfect phone-lock proof. This is social enforcement with visible
  unlock counts, which is acceptable for a low-stakes raffle and honest
  about its limits.
- No native app, no PyScript, no frontend build step.

## Run it locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/, create an event as a host, and join it
as a guest with the join code.

With Postgres locally, start `docker compose up db` and export the
`POSTGRES_*` values from `.env.example` before running migrate.

## Checks

```sh
python manage.py test
ruff check .
ruff format --check .
```

## Production checklist, not yet done

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS`
from the environment. Use managed Postgres with backups, at least two web
instances behind health checks, Redis caching for the leaderboard fragment,
a worker for raffles and emails, Sentry for errors, and idempotent Stripe
webhooks when billing is added. Do not run the dev secret key or SQLite
in production.

## Tooling source

Scaffolded from the Django Fundamentals starter tooling: `uv`-style
`pyproject.toml`, Ruff with Django rules, djLint for templates,
pytest-django, and an `AGENTS.md` for coding agents. Two deliberate
divergences from that course starter: this project runs on Python 3.12
in this environment (the starter targets 3.14), and migrations are
committed, because this is a product, not exercises.
