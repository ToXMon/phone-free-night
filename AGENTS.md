# Phone-Free Night

A Django site for trivia hosts. Hosts run weekly phone-free trivia nights.
Guests join by QR code, earn phone-free minutes, and enter sponsor raffles.

## Commands

- `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py runserver`
- These checks must all pass before a change is done:
  - `python manage.py test`
  - `ruff check .`
  - `ruff format --check .`

## Rules

- This project uses Django 5. No type hints, in any file, following the
  Django Fundamentals starter style.
- Do not add a frontend build step. HTMX and a small amount of inline
  JavaScript are the whole frontend.
- Points live in the database, not on a blockchain. Do not add a tradable
  token, a wallet requirement, or a blockchain call in a web request.
- Guests join without an account. A guest token in the URL is the only
  guest credential, and stakes are low: a raffle, not money.
- Hosts log in with Django auth. A host can only see and change their
  own events.
- Migrations are committed. The course starter excluded generated
  migrations because it was exercises. This is a product, so they stay.
- Do not add dependencies without a reason in the change description.
  Stripe, embedded wallets, and on-chain VRF are later stages, not v1.
