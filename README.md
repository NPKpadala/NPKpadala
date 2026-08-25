<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/main/assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/main/assets/header-light.svg">
  <img src="https://raw.githubusercontent.com/NPKpadala/NPKpadala/main/assets/header-dark.svg" alt="Praveen Kumar Padala — Infrastructure Operations &amp; Systems Engineer. Looping animation of the delivery pipeline: idea, blueprint, code, test, launch, orbit, real users, growth." width="100%">
</picture>

<sub>idea → blueprint → code → tests → launch → orbit → <b>real users</b> → <b>growth</b> · hand-authored SVG, no JavaScript and no third-party image service</sub>

<a href="https://npkpadala.com"><img src="https://img.shields.io/badge/portfolio-npkpadala.com-3FB950?style=flat-square&labelColor=161B22" alt="Portfolio"></a>
<a href="mailto:praveen.padala.2001@gmail.com"><img src="https://img.shields.io/badge/email-praveen.padala.2001-8B949E?style=flat-square&labelColor=161B22" alt="Email"></a>
<a href="https://github.com/NPKpadala?tab=followers"><img src="https://img.shields.io/github/followers/NPKpadala?style=flat-square&label=followers&color=8B949E&labelColor=161B22" alt="Followers"></a>

</div>

<!-- START_SECTION:banner -->
> 🟢 **All 2 monitored services operational** · probed `2026-08-25 04:57 UTC`
<!-- END_SECTION:banner -->

## About

I run infrastructure for production systems that other people depend on  provisioning, hardening,
monitoring, backups and recovery on Linux and Oracle Cloud. Most of what I build is the unglamorous
half: the deploy that doesn't need babysitting, the backup that gets verified, the alert that fires
before a client notices.

- **I operate what I ship.** Multi-tenant SaaS on OCI nginx, PM2, Docker, PostgreSQL per tenant, nightly verified dumps.
- **Automate anything done twice.** Cron-driven ops, self-healing services, scripted deploys, zero-touch alerting.
- **Observability I built rather than bought** — [Ops Monitor](https://github.com/NPKpadala/-ops-monitor) polls hosts and apps every 5s and pages me on Telegram.
- **AI where it earns its place.** LLM-backed extraction in [Job Alert Bot](https://github.com/NPKpadala/job-alert-bot) (Gemini), agent-assisted scripting and review across my own repos, and AI-drafted triage on alerts. Treated like any other dependency: rate-limited, cost-capped, and never the last word on a production change.
- **Document pipelines** — OCR and extraction frameworks that turn unstructured files into clean APIs.

Currently going deeper on distributed systems, multi-tenant architecture, performance work, and on where AI genuinely belongs in an ops loop — retrieval over runbooks, anomaly summaries, and agents that draft the fix while a human still approves it.

## Toolkit

| | |
|:---|:---|
| **Systems** | `Linux` `Oracle Linux` `Ubuntu` `RHEL` `systemd` `cron` `Bash` `Python` |
| **Serving** | `nginx` `Gunicorn` `PM2` `Docker` `FastAPI` `Flask` `Node.js` |
| **Data & async** | `PostgreSQL` `Redis` `Celery` |
| **Cloud & CI** | `Oracle Cloud Infrastructure` `Render` `GitHub Actions` `Telegram alerting` |
| **AI in the loop** | `Google Gemini` `Claude` `OCR / document extraction` `retrieval over runbooks` `agent-assisted scripting` |

## How it fits together

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/main/assets/topology-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/main/assets/topology-light.svg">
  <img src="https://raw.githubusercontent.com/NPKpadala/NPKpadala/main/assets/topology-dark.svg" alt="Production topology: nginx edge, app tier under PM2, Celery and Redis async workers, PostgreSQL per tenant — all watched by a self-built observability loop that pages Telegram" width="100%">
</picture>

</div>

<sub>Edge to storage, and the loop that watches all of it. The loop is <a href="https://github.com/NPKpadala/-ops-monitor">Ops Monitor</a> — read-only collectors, threshold evaluation, Telegram paging, live dashboard.</sub>

## Selected work

| Project | What it does | Stack |
|:---|:---|:---|
| [**PDFWala**](https://github.com/NPKpadala/pdfwala) | PDF-processing platform with an async job pipeline | `Flask` `Celery` `Redis` `Docker` |
| [**Ops Monitor**](https://github.com/NPKpadala/-ops-monitor) | App and infra monitoring, alerting and support tickets | `Node.js` `PM2` `Telegram` |
| [**Invoice API**](https://github.com/NPKpadala/invoice-api) | OCR-driven invoice extraction service | `FastAPI` `Tesseract` `OpenCV` |
| [**Job Alert Bot**](https://github.com/NPKpadala/job-alert-bot) | AI-assisted job alerts behind a rate-limited API | `FastAPI` `Gemini` |
| [**system_disk**](https://github.com/NPKpadala/system_disk) | Disk and I/O monitor that flags unused filesystems | `Python` `GitHub Actions` |
| [**Portfolio**](https://github.com/NPKpadala/npkpadala-portfolio) | Hand-built site — canvas animation, no build step | `HTML` `Canvas` `GSAP` |

## Live telemetry

<!-- START_SECTION:telemetry -->
<!-- probe:2026-08-25T04:57:25Z|Portfolio Website=up,PDFWala=up -->
> Probed from a GitHub Actions runner · **2/2 operational** · last check `2026-08-25 04:57 UTC`

| Service | Endpoint | Health | Latency |
|:---|:---|:---|:---|
| **Portfolio Website** | `npkpadala.com` | 🟢 `OPERATIONAL` `200` | `1476 ms` |
| **PDFWala** | `pdf.npkpadala.com/` | 🟢 `OPERATIONAL` `200` | `1518 ms` |

<sub>Two attempts before anything is called unreachable, and a run where every target fails is read as a broken prober, not a simultaneous outage.</sub>
<!-- END_SECTION:telemetry -->

<!-- LIVE STATUS (Upptime) — the table above is probed hourly from this repo and needs
     no extra setup. Upptime adds what a single hourly probe cannot: 5-minute
     resolution, 90-day uptime history, a hosted status page and automatic incident
     issues. Set it up with .github/upptime/SETUP.md, then uncomment this block.
     Kept commented so the profile never renders broken badge images.

### Live system status

| System | Status | Uptime (30d) | Response |
|:---|:---|:---|:---|
| **Portfolio Website** | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/portfolio-website/status.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/portfolio-website/uptime-30.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/portfolio-website/response-time.json&style=flat-square) |
| **PDFWala** | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/pdfwala/status.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/pdfwala/uptime-30.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/pdfwala/response-time.json&style=flat-square) |

<sub>Probed every 5 minutes from GitHub Actions · <a href="https://npkpadala.github.io/upptime/">full history →</a></sub>
-->

## Recent activity

<!-- START_SECTION:activity -->
```text
  16d ago  pr      npkpadala-portfol… #1 merged
  19d ago  pr      npkpadala-portfol… #1 opened
  19d ago  create  npkpadala-portfol… branch claude/hero-idea-to-orbit
  19d ago  pr      NPKpadala          #4 merged
  19d ago  pr      NPKpadala          #4 opened
  19d ago  create  NPKpadala          branch claude/hero-idea-to-growth
```
<sub>Synced 2026-08-25 09:54 UTC · refreshed every 6h by GitHub Actions.</sub>
<!-- END_SECTION:activity -->

<!-- Optional: add a WAKATIME_API_KEY repo secret and this fills with last-7-day language stats. -->
<!-- START_SECTION:waka -->
<!-- END_SECTION:waka -->

<details>
<summary>GitHub stats</summary>

<br>

<div align="center">

<img height="160" src="https://github-readme-stats.vercel.app/api?username=NPKpadala&show_icons=true&include_all_commits=true&count_private=true&hide_border=true&bg_color=00000000&title_color=3FB950&icon_color=3FB950&text_color=8B949E" alt="GitHub stats">
<img height="160" src="https://github-readme-stats.vercel.app/api/top-langs/?username=NPKpadala&layout=compact&hide_border=true&bg_color=00000000&title_color=3FB950&text_color=8B949E&langs_count=8" alt="Top languages">

</div>

<sub>Served by a public github-readme-stats instance — it rate-limits, which is exactly why it lives behind this toggle instead of at the top of the page.</sub>

</details>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/output/github-contribution-grid-snake.svg">
  <img alt="Contribution grid" src="https://raw.githubusercontent.com/NPKpadala/NPKpadala/output/github-contribution-grid-snake-dark.svg" width="100%">
</picture>

<br><br>

<sub>Header and topology are hand-authored SVG in <a href="https://github.com/NPKpadala/NPKpadala/blob/main/.github/scripts/build_assets.py"><code>build_assets.py</code></a> · telemetry and activity are written by <a href="https://github.com/NPKpadala/NPKpadala/tree/main/.github/workflows">scheduled Actions</a> · nothing on this page is hand-edited.</sub>

</div>
