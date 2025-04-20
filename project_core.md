# PM Agent – **Complete End‑to‑End Project Scope & User Journey**

**Vision:** A chat‑first web app that automates your PM workflow—planning, risk check‑ins, scheduling, alerts, logging, and reporting—with a future AI‑face & voice upgrade.

---

## 1 ▸ Core Objectives

1. **Project Scoping & Planning**  
2. **Risk‑Based Check‑Ins & Meeting Scheduling**  
3. **Daily Overdue Alerts**  
4. **Living Project Log**  
5. **Stakeholder Progress Reporting**  
6. **On‑Demand Triage Meeting Scheduler**  
7. **Future: AI Face & Voice Interface**

---

## 2 ▸ Feature Breakdown & User Journey

### 2.1 Project Scoping & Planning (`/plan`)

- **User** types in‑app chat:  
  ```
  /plan Redesign landing page by Sep‑05; Dev: Alice,Bob; Mktg: Carol
  ```
- **System**  
  1. Parses via LLM → `plan.json` (stories, owners, due‑dates).  
  2. Renders **Kanban board** (Backlog/Doing/Done) + **Gantt chart**.  
  3. Stores plan in DB.  
  4. Sends personalized emails to Alice, Bob, Carol:  
     > “Please review your assigned stories, create subtasks, and let me know any blockers.”

### 2.2 Risk‑Based Check‑Ins & Meeting Scheduling (`/risk` + `/schedule`)

- **Trigger**: PM types `/risk` or clicks “Risk Check‑In.”
- **Modal Delivery**:  
  - **System** sends the modal **to all Team Leads** via DM or in‑app notification.  
  - Modal lists each of their active stories with a **Yes/No “On Track?”** toggle and a multi‑choice for “Need Discussion” / “Missing Estimated Completion.”
- **Team Lead Response**:  
  - For each story, Lead selects:  
    - **Yes** → no action  
    - **No** → flagged as blocker  
    - **Need Discussion** or **Missing Estimated Completion** → in addition to flagging, **each such Lead receives a personalized calendar invite** for the next day’s stand‑up/scrum meeting.  
- **System Actions**:  
  1. Any story marked **No** turns red on the board.  
  2. Immediate PM alert:  
     > “🚨 Blocker on story #X reported by `<Lead>`.”  
  3. For “Need Discussion” / “Missing Estimated Completion,” personalized meeting invites created for the next day’s stand‑up and sent to the respective Lead(s).

### 2.3 Daily Overdue Alerts (`/alerts`)

- **Cron** at 07:45 AM (or manually `/alerts`):  
  - Scans each card’s due‑date vs. status.  
  - For any overdue card: sends DM/in‑app ping to the owner:  
    > “⚠️ Your task ‘…’ is overdue by X days.”  
  - Populates “Today’s Alerts” panel in UI.

### 2.4 Living Project Log (`/log`)

- After every `/plan`, `/risk`, `/schedule`, and `/alerts` run:  
  - Appends a timestamped entry to the **Project Log** page (in‑app or via Notion API), e.g.:  
    ```
    [2025‑04‑21 09:01] /plan executed – board & Gantt created.
    [2025‑04‑22 10:05] /risk – Alice reported blocker on story #2.
    [2025‑04‑22 10:06] PM alerted of blocker.
    [2025‑04‑22 10:10] /schedule – Meeting scheduled for 10:15–10:30.
    [2025‑04‑23 07:45] /alerts – Bob’s ‘hero banner’ overdue.
    ```

### 2.5 Stakeholder Progress Report (`/digest`)

- **User** clicks “Generate Digest” or types `/digest`.  
- **System**  
  1. Aggregates board data & log.  
  2. Creates:  
     - Status vs. plan summary  
     - Burndown chart  
     - Blocker overview  
  3. Renders PDF via Pandoc or Puppeteer.  
  4. Prompts PM “Approve to send?” → on click, emails to stakeholders.

### 2.6 On‑Demand Triage Meeting Scheduler (`/schedule`)

- **User** types `/schedule` (or auto‑trigger when ≥ 3 blockers).  
- **System**  
  1. Gathers all blocked stories.  
  2. Checks in‑app calendar for earliest 15 min free slot for PM + affected Leads.  
  3. Creates meeting event (Google Calendar API) & returns invite link.

---

## 3 ▸ Cheat‑Sheet of Commands

| Command      | Description                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------|
| `/plan`      | Kick‑off project: generate Kanban + Gantt, email owners.                                              |
| `/risk`      | Send risk check‑in modal to Leads; flag blockers & schedule invites for “Need Discussion” responses.  |
| `/alerts`    | Trigger today’s overdue‑task pings to owners.                                                         |
| `/schedule`  | Schedule a 15 min triage meeting for blocked stories.                                                 |
| `/digest`    | Generate & send weekly PDF status report to stakeholders.                                             |
| `/log`       | View the chronological Project Log entries.                                                           |

---

## 4 ▸ Architecture Overview

```
Client (Next.js + React)           Server (FastAPI + LangChain)
──────────────────                 ───────────────────────────────
┌──────────────────────────┐        ┌─────────────────────────┐
│ Chat UI & Boards UI      │◀──────▶│ /chat  endpoint        │
│ Risk Modal & Alerts UI   │        │ /plan, /risk, /alerts, │
│ Digest & Log pages       │        │ /schedule, /digest, /log│
└───────┬──────────────────┘        └──────────┬──────────────┘
        ▼                              Tools & DB ▼
┌─────────────────────┐ modals/pings ┌────────────────────────┐
│ Scheduler (apscheduler)───────────>│  Notion API or SQLite  │
│                     │              │  Email/Calendar API    │
└─────────────────────┘              └────────────────────────┘
```

---

## 5 ▸ Tech Stack

| Layer                  | Technology / Library                              |
|------------------------|---------------------------------------------------|
| **Frontend**           | Next.js, React, Tailwind CSS                      |
| **Backend**            | FastAPI, Uvicorn, LangChain                       |
| **LLM**                | GPT‑4 via OpenAI or `llama-cpp-python` + Llama‑3   |
| **DB**                 | SQLite + SQLModel                                 |
| **Kanban & Log**       | In‑app React or Notion API                        |
| **Scheduling**         | `apscheduler`, Google Calendar API                |
| **Charting**           | Mermaid CLI, Chart.js                              |
| **PDF Generation**     | Pandoc or Puppeteer (HTML→PDF)                    |
| **Alerts/Comm**        | Slack Bolt SDK, SMTP/SendGrid, Email, In‑app UI    |

---

## 6 ▸ 15‑Hour Development Timeline

| Time         | Deliverable                                  |
|--------------|----------------------------------------------|
| **0–1 h**    | Scaffold Next.js & FastAPI, env config       |
| **1–3 h**    | `/plan` → LLM parsing + Kanban + Gantt       |
| **3–5 h**    | `/risk` modal → blocker flags + invites      |
| **5–6 h**    | `/alerts` cron job for overdue pings         |
| **6–7 h**    | `/log` Project Log append & view            |
| **7–9 h**    | `/digest` PDF gen + approval UI              |
| **9–10 h**   | `/schedule` triage meeting flow              |
| **10–12 h**  | UI polish, error handling, prompt tuning     |
| **12–14 h**  | Integrations (Calendar, Email, Notion)       |
| **14–15 h**  | Demo prep, slides, recording, deploy scripts |

---

## 7 ▸ Future Phase: AI Face & Voice

1. **Avatar Component**  
   - Embed a living avatar via Pixela AI SDK or Three.js canvas.  
2. **Speech Interface**  
   - Replace chat input with Mic button + Whisper STT + Web‑TTS responses.  
3. **Personalization**  
   - Memory of user names, project preferences, greeting messages.

---

## 8 ▸ Demo Pitch Script (3 min)

> **“Welcome to SyncSphere Web—the only PM portal you need.**  
> **Step 1:** `/plan` to spin up your project board and Gantt in seconds.  
> **Step 2:** Click **Risk Check‑In** to collect stand‑up statuses; any “No” or “Needs Discussion” flags blockers and auto‑schedules a meeting only with relevant leads.  
> **Step 3:** Use `/alerts` for daily overdue pings to task owners.  
> **Step 4:** Click **Generate Digest** to produce your executive PDF for stakeholders.  
> **Step 5:** View the **Project Log** for a complete action history.  
> All in one webapp—ready for your future AI‑face and voice interface.”  

This end‑to‑end scope delivers a **fully automated PM workflow** in 15 hours, satisfying every user journey point and paving the way for an AI‑driven future.