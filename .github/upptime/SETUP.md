# Live status badges — one-time setup

The README ships with a **Live System Status** table already written, but kept
inside an HTML comment so the profile never shows broken images. Upptime runs
from its *own* repository, which only you can create — these are the steps, and
then you uncomment the block.

Budget ten minutes.

---

## 1. Create the Upptime repo

1. Go to <https://github.com/upptime/upptime> and click **Use this template →
   Create a new repository**.
2. Name it exactly **`upptime`** (owner `NPKpadala`), and make it **public** —
   the README badges read raw JSON from it, which requires public visibility.

## 2. Drop in the config

Copy [`.upptimerc.yml`](./.upptimerc.yml) from this folder to the **root** of
that new repo, then edit it:

- Replace the two `REPLACE-ME` URLs (PDFWala, Invoice API) with the real public
  endpoints, or delete those entries.
- Prefer a cheap, unauthenticated health endpoint over a homepage — it makes
  response-time graphs mean something.

## 3. Add the token

Upptime commits results back and opens incident issues, so `GITHUB_TOKEN` is not
enough:

1. Create a fine-grained or classic PAT with the **`repo`** and **`workflow`**
   scopes.
2. In the `upptime` repo: **Settings → Secrets and variables → Actions → New
   repository secret**, name it **`GH_PAT`**, paste the token.

## 4. Turn on what it needs

In the `upptime` repo's settings:

- **Issues** — enabled (incidents are issues).
- **Actions** — enabled, with **Read and write permissions** under
  *Settings → Actions → General → Workflow permissions*.
- **Pages** — source `gh-pages` branch, if you want the hosted status site.

Then run the **Uptime CI** workflow once from the Actions tab instead of waiting
for the schedule.

## 5. Light up the badges

Once `api/portfolio/status.json` exists in the `upptime` repo, open this
profile's `README.md`, find:

```
<!-- LIVE STATUS — uncomment after Upptime setup -->
```

…and delete the `<!--` / `-->` around the table below it. Slugs come from the
`name` field, lowercased and hyphenated (`Invoice API` → `invoice-api`), so keep
those names stable or the badge URLs 404.

---

### Why the badges are worth the ten minutes

Anyone can list "monitoring" on a CV. A green badge that a hiring manager can
click through to a 90-day uptime history is the version they believe — and it is
measured by an independent runner, not self-reported.
