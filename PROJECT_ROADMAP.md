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

### Sprint 2: Job Discovery & Description Parsing
- **Goals:** Setup Event Bus (Redis) and implement Module 4 (JD Intelligence Engine).
- **Deliverables:**
  - Initialize the Redis event broker and publisher/subscriber interfaces.
  - Implement raw HTML job post scraping from portals.
  - Parse job title, company, description details, and experience keywords into structured JSON.
- **Milestone:** Emitting `job.discovered` publishes an event that resolves to a cleanly structured `jd.parsed` message.

### Sprint 3: Match Engine & Resume Intelligence
- **Goals:** Implement Module 3 (Resume Intelligence Engine) and Module 5 (Matching Engine).
- **Deliverables:**
  - Build the matching engine using heuristics first, then falling back to LLM calls.
  - Extract text segments from resume files (PDF/DOCX).
  - Tailor resume files by restructuring highlights and project keywords to match specific JD requirements.
- **Milestone:** Evaluation score generated for parsed job descriptions; tailored resumes generated in the output directory.

### Sprint 4: Adaptive Browser Automation & Applications
- **Goals:** Implement Module 6 (Browser Automation Engine) and Module 7 (Application Engine).
- **Deliverables:**
  - Implement the Playwright Chromium controller using persistent browser profiles.
  - Set up the Adaptive Browser Agent (inspections via accessibility roles and labels).
  - Code application handlers for ATS portals (LinkedIn Easy Apply, Workday, Lever, Greenhouse).
  - Implement MFA/CAPTCHA intervention hooks.
- **Milestone:** Auto-fill form interfaces dynamically on testing pages and submit test applications.

### Sprint 5: Tracking, Alerts & Feedback Loops
- **Goals:** Implement Module 8 (Tracking Engine), Module 9 (Notification Engine), and Module 10 (Learning Engine).
- **Deliverables:**
  - Write SQL logic to track applications across states in PostgreSQL.
  - Wire alerts to Slack, WhatsApp, or Telegram webhooks.
  - Implement the Learning feedback loops which refine match priorities based on outcomes.
- **Milestone:** Unified dashboard, live notifications, and pipeline analytics reporting running on the server.
