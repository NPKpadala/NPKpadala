<!-- ============ HERO ============ -->
<div align="center">

<a href="https://npkpadala.com">
  <img src="https://readme-typing-svg.demolab.com/?lines=Hi%2C+I'm+Praveen+Kumar+Padala+%F0%9F%91%8B;Infrastructure+Operations+%26+Systems+Engineer+%F0%9F%9B%A0%EF%B8%8F;DevOps+%26+Automation+Specialist+%F0%9F%9A%80&font=Fira+Code&weight=600&center=true&width=600&height=60&color=39FF14&vCenter=true&pause=1000&size=22&background=00000000" alt="Praveen Kumar Padala — Infrastructure Operations & Systems Engineer" />
</a>

<br/>

<a href="https://npkpadala.com"><img src="https://img.shields.io/badge/Portfolio-npkpadala.com-39FF14?style=flat-square&logo=googlechrome&logoColor=black&labelColor=0D1117" alt="Portfolio"/></a>
&nbsp;
<a href="mailto:praveen.padala.2001@gmail.com"><img src="https://img.shields.io/badge/Email-praveen.padala.2001-00E5FF?style=flat-square&logo=gmail&logoColor=black&labelColor=0D1117" alt="Email"/></a>
&nbsp;
<a href="https://github.com/NPKpadala?tab=followers"><img src="https://img.shields.io/github/followers/NPKpadala?style=flat-square&logo=github&label=Follow&color=39FF14&labelColor=0D1117" alt="GitHub followers"/></a>
&nbsp;
<img src="https://komarev.com/ghpvc/?username=NPKpadala&style=flat-square&color=39FF14&label=Profile+Views" alt="Profile views"/>

</div>

<br/>

<!-- ============ OPS BANNER ============ -->
<!-- START_SECTION:banner -->
```console
[ OPS TELEMETRY — npkpadala ]
------------------------------------------------------------------------------
HOST        : Oracle Cloud Infrastructure · Oracle Linux (aarch64)
RUNTIME     : PM2 process manager · Docker · nginx reverse proxy
DATA        : PostgreSQL (per-tenant) · Redis · Celery workers
OBSERVE     : self-built Ops Monitor · 5s host+app polling · Telegram paging
STATUS      : 🟢 ALL 2 MONITORED SERVICES OPERATIONAL
LAST PROBE  : 2026-08-05 10:00 UTC
------------------------------------------------------------------------------
```
<!-- END_SECTION:banner -->

<br/>

<!-- ============ ABOUT ============ -->

## ⚡ About Me

```bash
$ whoami
```

> **Infrastructure Operations & Systems Engineer** who treats every system like production — because it is.

- 🖥️ Manage **high-availability server infrastructure** end to end: provisioning, hardening, monitoring, backups and disaster recovery on Linux/Cloud ecosystems
- 🤖 **Automate everything twice-done** — cron-driven ops, self-healing services, scripted deploys and zero-touch alerting pipelines
- 📄 Build **data-extraction frameworks** — OCR/document pipelines that turn unstructured files into clean, structured APIs
- 📈 Obsessed with **observability** — I built my own ops platform that watches every app and server I run (uptime, disk, deploys, tickets)
- 🧪 Currently deepening: distributed systems, multi-tenant SaaS architecture and performance engineering
- 📫 Reach me at **praveen.padala.2001@gmail.com** · [npkpadala.com](https://npkpadala.com)

<br/>

<!-- ============ TECH STACK ============ -->

## 🧰 Core Tech Stack

<div align="center">

**⚙️ Core Systems & Scripting**

<a href="https://skillicons.dev"><img src="https://skillicons.dev/icons?i=linux,ubuntu,redhat,bash,python&theme=dark" alt="Linux · Ubuntu · RHEL/CentOS · Bash · Python"/></a>
<br/>
<img src="https://img.shields.io/badge/systemd-0D1117?style=flat-square&logo=linux&logoColor=39FF14" alt="systemd"/>
<img src="https://img.shields.io/badge/cron-0D1117?style=flat-square&logo=gnubash&logoColor=39FF14" alt="cron"/>
<img src="https://img.shields.io/badge/Hardening%20%26%20Backups-0D1117?style=flat-square&logo=letsencrypt&logoColor=39FF14" alt="Hardening & Backups"/>

**🌐 Web Architectures & APIs**

<a href="https://skillicons.dev"><img src="https://skillicons.dev/icons?i=fastapi,flask,nodejs,nginx,redis,postgres&theme=dark" alt="FastAPI · Flask · Node.js · Nginx · Redis · PostgreSQL"/></a>
<br/>
<img src="https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white" alt="Gunicorn"/>
<img src="https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white" alt="Celery"/>
<img src="https://img.shields.io/badge/REST%20APIs-00E5FF?style=flat-square&logo=swagger&logoColor=black" alt="REST APIs"/>

**☁️ Infrastructure & DevOps**

<a href="https://skillicons.dev"><img src="https://skillicons.dev/icons?i=docker,githubactions,git,github&theme=dark" alt="Docker · GitHub Actions · Git · GitHub"/></a>
<br/>
<img src="https://img.shields.io/badge/Oracle%20Cloud%20Infrastructure-F80000?style=flat-square&logo=oracle&logoColor=white" alt="Oracle Cloud Infrastructure"/>
<img src="https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black" alt="Render"/>
<img src="https://img.shields.io/badge/PM2-2B037A?style=flat-square&logo=pm2&logoColor=white" alt="PM2"/>
<img src="https://img.shields.io/badge/Telegram%20Alerting-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Telegram alerting"/>

</div>

<br/>

<!-- ============ TOPOLOGY ============ -->

## 📐 Production Topology

How the pieces actually fit together — edge to storage, and the loop that watches all of it.

```text
                              ┌───────────────────────────┐
                              │  EDGE / TLS TERMINATION   │
                              │  nginx (Docker) · certbot │
                              │  rate limits · /ops proxy │
                              └─────────────┬─────────────┘
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        ▼                                   ▼                                   ▼
┌────────────────────┐          ┌────────────────────────┐          ┌────────────────────┐
│   API / APP TIER   │          │   ASYNC PROCESSING     │          │   MANAGED / PaaS   │
│  FastAPI · Flask   │          │  Celery workers        │          │  Render-hosted     │
│  Node.js · Gunicorn│─ enqueue▶│  Redis broker          │          │  services          │
│  under PM2         │◀ result ─│  (PDFWala pipeline)    │          │  (Invoice API)     │
└─────────┬──────────┘          └───────────┬────────────┘          └─────────┬──────────┘
          │                                 │                                 │
          └─────────────────┬───────────────┘                                 │
                            ▼                                                 │
                 ┌─────────────────────┐                                      │
                 │    PERSISTENCE      │                                      │
                 │ PostgreSQL per      │                                      │
                 │ tenant · nightly    │                                      │
                 │ pg_dump + verify    │                                      │
                 └──────────┬──────────┘                                      │
                            │                                                 │
   ═════════════════════════╪═════════════════════════════════════════════════╪══════
                            ▼            OBSERVABILITY LOOP                    ▼
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │  collector  ──5s host+app · 30s deep · 4s logs──▶  ingest API  ──▶  Postgres  │
   │      │ read-only, execFile only                        │                      │
   │      └── pm2 · docker · psql · logs · TLS              ▼                      │
   │                                            threshold eval → alerts → Telegram │
   │                                                        │                      │
   │                                          WebSocket ────┴──▶ live NOC dashboard│
   └──────────────────────────────────────────────────────────────────────────────┘
```

<sub>The observability loop is <a href="https://github.com/NPKpadala/-ops-monitor">Ops Monitor</a> — built and operated in-house rather than bought.</sub>

<br/>

<!-- ============ PRODUCTION SYSTEMS ============ -->

## 🚀 Production Systems I Built & Operate

<div align="center">

| System | Purpose | Stack |
|:---|:---|:---|
| 🗂️ [**PDFWala**](https://github.com/NPKpadala/pdfwala) | Scalable PDF-processing platform — async pipeline architecture | `Flask` `Celery` `Redis` `Docker` |
| 📡 [**Ops Monitor**](https://github.com/NPKpadala/-ops-monitor) | Self-built app + infra monitoring, alerting & support-ticket platform | `Node.js` `PM2` `Telegram` |
| 🧾 [**Invoice API**](https://github.com/NPKpadala/invoice-api) | OCR-powered invoice data-extraction framework | `FastAPI` `Tesseract` `OpenCV` |
| 🔔 [**Job Alert Bot**](https://github.com/NPKpadala/job-alert-bot) | AI-assisted job-alert service with secured, rate-limited API | `FastAPI` `Google Gemini` |
| 💾 [**system_disk**](https://github.com/NPKpadala/system_disk) | Disk-usage & I/O monitor that flags unused filesystems | `Python` `GitHub Actions` |
| 🌐 [**Portfolio**](https://github.com/NPKpadala/npkpadala-portfolio) | Hand-built portfolio — canvas animations, zero build step | `HTML` `Canvas` `GSAP` |

</div>

<br/>

### 📡 Infrastructure Telemetry

<!-- START_SECTION:telemetry -->
<!-- probe:2026-08-05T10:00:07Z|Portfolio Website=up,PDFWala=up -->
> Probed from a GitHub Actions runner · **2/2 operational** · last check `2026-08-05 10:00 UTC`

| Service | Endpoint | Health | Latency |
|:---|:---|:---|:---|
| **Portfolio Website** | `npkpadala.com` | 🟢 `OPERATIONAL` `200` | `1275 ms` |
| **PDFWala** | `pdf.npkpadala.com/` | 🟢 `OPERATIONAL` `200` | `1481 ms` |

<sub>Two attempts before anything is called unreachable, and a run where <em>every</em> target fails is treated as a broken prober rather than a simultaneous outage. API-first hosts are judged on reachability, so a <code>404</code> at <code>/</code> reads green — the origin answered and routed. A <code>5xx</code> does not.</sub>
<!-- END_SECTION:telemetry -->

<!-- LIVE STATUS (Upptime) — the table above is probed hourly from this repo and needs
     no extra setup. Upptime adds what a single hourly probe cannot: 5-minute
     resolution, 90-day uptime history, a hosted status page and automatic incident
     issues. Set it up with .github/upptime/SETUP.md, then uncomment this block.
     Kept commented so the profile never renders broken badge images.

### 🟢 Live System Status

<div align="center">

| System | Status | Uptime (30d) | Response |
|:---|:---|:---|:---|
| **Portfolio Website** | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/portfolio-website/status.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/portfolio-website/uptime-30.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/portfolio-website/response-time.json&style=flat-square) |
| **PDFWala** | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/pdfwala/status.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/pdfwala/uptime-30.json&style=flat-square) | ![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/NPKpadala/upptime/master/api/pdfwala/response-time.json&style=flat-square) |

<sub>Probed every 5 minutes from GitHub Actions · <a href="https://npkpadala.github.io/upptime/">full history →</a></sub>

</div>
-->

<br/>

<!-- ============ LIVE OPS DASHBOARD ============ -->

## 📊 Live Ops Dashboard

<sub>Everything below is generated by scheduled GitHub Actions in this repo — nothing here is hand-edited.</sub>

### 📡 Activity stream

<!-- START_SECTION:activity -->
```console
$ npk-ops --tail activity --user NPKpadala

  15h ago  pr      NPKpadala          #2 merged
  15h ago  pr      NPKpadala          #2 opened
  16h ago  pr      NPKpadala          #1 merged
  16h ago  pr      NPKpadala          #1 opened
  16h ago  create  NPKpadala          branch claude/readme-hiring-mana…
   8d ago  create  -sudo-access-trac… branch main
   8d ago  pr      system_disk        #3 merged
   8d ago  pr      -ops-monitor       #1 merged

# stream synced 2026-08-05 10:00 UTC · refreshed every 6h by GitHub Actions
```
<!-- END_SECTION:activity -->

<!-- Optional: add a WAKATIME_API_KEY repo secret and this fills with last-7-day language stats. -->
<!-- START_SECTION:waka -->
<!-- END_SECTION:waka -->

### 📈 Contribution metrics

<div align="center">

<!-- Public github-readme-stats instances are aggressively rate-limited; if these
     ever render as broken images, self-host the service and swap the hostname. -->
<img height="170" src="https://github-readme-stats.vercel.app/api?username=NPKpadala&show_icons=true&include_all_commits=true&count_private=true&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=39FF14&icon_color=00E5FF&text_color=C9D1D9" alt="GitHub profile summary stats"/>
<img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username=NPKpadala&layout=donut&theme=tokyonight&hide_border=true&bg_color=0D1117&title_color=39FF14&text_color=C9D1D9&langs_count=8" alt="Top languages donut chart"/>

<br/><br/>

<img src="https://streak-stats.demolab.com?user=NPKpadala&theme=tokyonight&hide_border=true&background=0D1117&ring=39FF14&fire=00E5FF&currStreakLabel=39FF14&sideLabels=C9D1D9&dates=8B949E" alt="GitHub streak counter"/>

<br/><br/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=NPKpadala&theme=github-compact&hide_border=true&bg_color=0D1117&color=C9D1D9&line=39FF14&point=00E5FF&area=true&area_color=39FF14" alt="Contribution activity graph"/>

</div>

### 🐍 Contribution grid

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/NPKpadala/NPKpadala/output/github-contribution-grid-snake.svg">
  <img alt="Contribution grid being eaten by a snake" src="https://raw.githubusercontent.com/NPKpadala/NPKpadala/output/github-contribution-grid-snake-dark.svg">
</picture>

<sub>Rendered twice daily by <a href="https://github.com/NPKpadala/NPKpadala/blob/main/.github/workflows/snake.yml"><code>snake.yml</code></a> · snake <code>#00E5FF</code>, trail <code>#39FF14</code></sub>

</div>

<br/>

<!-- ============ FOOTER ============ -->

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0D1117,50:39FF14,100:00E5FF&height=100&section=footer" alt="" width="100%"/>

<i>“Ship it. Monitor it. Own it.”</i>

</div>
