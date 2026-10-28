# Deploy with a Neon database

Yes: keep the database on Neon and put only the app container somewhere
cheap. That is the cheapest shape for this app, because it deletes the
managed-Postgres line from every app host's bill.

## The shape

- App: one container, Fly.io, Render, Railway, or Akash. No database
  service on that host at all.
- Database: one Neon project for production, one for test. Or one Neon
  project with a `main` branch for production and a branch for test.
  Do not point test and production at the same database.
- Cost, roughly, at early trivia-host traffic:
  - Fly.io app, 512MB: about $3.69/month, plus Neon Free $0, or Neon
    Launch pay-as-you-go with no monthly minimum since December 2025.
  - Render paid app, 512MB: $7/month, plus Neon Free $0.
  - Akash app: about $1–3/month, plus Neon Free $0.
  - Neon Launch, when you outgrow Free: $0.106 per CU-hour and
    $0.35 per GB-month of storage. A database that scales to zero
    overnight only bills for the hours it actually ran.

## Configure one Neon database

1. In the Neon console, open the project you want for production.
2. On the branch you will use, create a database for this app, for
   example `phonefree_prod`. Use the other starter database, or a
   branch of the same project, for test, for example `phonefree_test`.
3. Click Connect, choose the pooled connection, and copy the
   connection string. The pooled host ends in `-pooler.neon.tech`.
   Use the pooler for a web app: Django plus HTMX polling plus more
   than one worker will otherwise hold too many direct connections.
4. Do not commit the connection string. Put it in the app host's
   secrets as `DATABASE_URL`, for example:
   `postgresql://user:password@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require`
5. Set the other production secrets on the same host:
   `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS`
   with the app's domain.
6. Run migrations once, from the deployed app or a one-off job:
   `python manage.py migrate`, then `python manage.py createsuperuser`.

## What the app already does for Neon

`config/settings.py` reads `DATABASE_URL` first, then `POSTGRES_*` /
`PG*` (the variables Neon shows in its console), then falls back to
local SQLite. On any `*.neon.tech` host it sets `sslmode=require`,
`DISABLE_SERVER_SIDE_CURSORS=True`, and `CONN_HEALTH_CHECKS=True`,
which is Neon's own Django guidance for pooled, scale-to-zero
connections.

## Two Neon gotchas to plan for

- Scale to zero: Neon suspends compute after about 5 minutes idle on
  Free and Launch. The first request after idle wakes the database
  and can take a few seconds. For a live trivia night, do not rely on
  a cold database: open the host dashboard or the first guest page a
  few minutes before the night, or on Launch set the compute not to
  scale to zero for the event window.
- Free limits: Free is 100 CU-hours per project per month and 0.5 GB
  of storage per project, with autoscaling up to 2 CU. That is plenty
  for weekly trivia at the start and for a test database, but it is
  not a production guarantee. When a night starts hitting the cap,
  move that one project to Launch, pay-as-you-go, and keep the test
  database on Free.
