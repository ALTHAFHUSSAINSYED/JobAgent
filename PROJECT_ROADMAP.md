# JobPilot AI Project Roadmap

This roadmap documents the phased implementation plan and module standards for **JobPilot AI** across 5 distinct sprints.

---

## Module Standard Layout

Every module implemented in the backend directory (`backend/app/<module_name>/`) must strictly adhere to the following architecture pattern:

```text
backend/app/<module_name>/
│
├── README.md            # Module summary, interfaces, and quickstart commands
├── architecture.md      # Detail design of execution steps, classes, and loops
├── models.py            # Pydantic schemas or DB model files
├── services.py          # Core business/reasoning logic (independent functions/classes)
├── workers.py           # Event handlers, queue subscribers/publishers
├── exception.py         # Custom module exceptions
└── tests/               # Unit and integration pytest files
```

---

## Phased Sprint Plan

### Sprint 1: Configuration & Identity Core
- **Goals:** Implement Module 1 (Configuration Engine) and Module 2 (Identity Engine).
- **Deliverables:**
  - Setup of runtime configuration parsing (YAML profiles) and validation (Pydantic).
  - Load environment values from local `.env`.
  - Secure credential loading and validation of candidate detail file structures.
- **Milestone:** CLI system starts up, validates `profile.yaml` schema, parses credentials, and runs verification checks.

### Sprint 2: Job Discovery & Intelligence
- **Goals:** Establish the discovery backend and intelligent candidate matching pipeline.
- **Sub-sprints:**
  - **Sprint 2.1 (Job Discovery Engine):** Build provider interface (`IJobProvider`) and implement Lever/Greenhouse public JSON API pullers, hourly scheduler pipelines, duplicate hashing, and rule-based candidate match scoring.
  - **Sprint 2.2 (JD Intelligence):** Integrate OpenRouter LLM parsing job descriptions into structured metadata (responsibilities, missing skills, keywords, ATS score).
  - **Sprint 2.3 (Resume Intelligence):** Implement AI-based resume picker, custom resume tailored outputs, and cover letters generation.
  - **Sprint 2.4 (Application Queue):** Define the queue pipeline classification states: Apply, Skip, and Manual Review.
  - **Sprint 2.5 (Browser Automation):** Initialize Playwright integrations only for final form fill auto-submits.
- **Milestone:** Scraped jobs visible in dashboard list; duplicate checks and candidate match scores showing in the UI.

### Sprint 3: Resume Intelligence & Form-Filling Automation
- **Goals:** Automate ATS resume tailoring and persistent form-filler actions.
- **Deliverables:**
  - Build PDF/DOCX resume generator parsing targeted keywords.
  - Create Playwright form fillers mapping accessibility roles/labels inside target portals (Greenhouse, Lever, LinkedIn).
- **Milestone:** Browser automation successfully populates and submits applications via queue items.

### Sprint 4: Interview Preparation & CRM Recruiter Tracking
- **Goals:** Build candidate interview trainer and recruiter feedback dashboards.
- **Deliverables:**
  - Create mock interview Q&A generation matching applied JDs.
  - Add recruiter application tracking status tables.
- **Milestone:** Recruiter database entries tracked across Applied, Interviewing, Offered, Rejected states.

### Sprint 5: Analytics, Alerts & Feedback Loops
- **Goals:** Implement Slack notifications and match tuning.
- **Deliverables:**
  - Build Slack/Telegram alerts channels mapping job status change updates.
  - Implement feedback learning loop tuning match heuristics weights based on recruiter responses.
- **Milestone:** Fully autonomous recruiter platform operating in production on EC2.

